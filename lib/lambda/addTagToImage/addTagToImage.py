import json
import boto3
import os
from datetime import datetime, timezone
from botocore.exceptions import ClientError

table_name = os.environ["TABLE_NAME"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)
client = boto3.client('dynamodb')

"""
Input: JSON object of form 
{
    "image_id": string, with the form "hash"
    "tag_id": string, with the form "tagname"
} 

Behavior:
inserts an entry into the db with primary_id = image_id and secondary_id = tag_id
increments tag_count on image if a new relation is added

Response:
http response with status of request
200 if image-tag addition was successful
400 if input error or if relation already exists
"""
def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        if not body:
            raise Exception
    except:
        return {
            'statusCode': 400,
            'body': json.dumps('Empty or invalid request body')
        }
    if 'image_id' not in body or 'tag_id' not in body:
        return {
            'statusCode': 400,
            'body': json.dumps('image_id and tag_id must both be in request')
        }
    image_id = body['image_id']
    tag_id = body['tag_id']
    created_at = datetime.now(timezone.utc).isoformat(timespec='seconds')

    # check if image and tag exist before creating relation
    try:
        validate_item_exists(image_id)
        validate_item_exists(tag_id)
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps(str(e))
        }  

    relation_item = {
        'primary_id': {'S': image_id},
        'secondary_id': {'S': tag_id},
        'item_type': {'S': 'relation'},
        'created_at': {'S': created_at}
    }

    try:
        response = client.transact_write_items(
            TransactItems = [
                # increment tag count for image
                {
                    'Update': {
                        'TableName': table_name,
                        'Key': {
                            'primary_id': {'S': image_id},
                            'secondary_id': {'S': image_id}
                        },
                        'UpdateExpression': 'ADD tag_count :inc',
                        'ExpressionAttributeValues': {
                            ':inc': {'N': '1'}
                        }
                    }
                },
                # add relation if relation does not already exist
                {
                    'Put': {
                        'TableName': table_name,
                        'Item': relation_item,
                        'ConditionExpression': 'attribute_not_exists(primary_id) OR attribute_not_exists(secondary_id)'
                    }
                }
            ]
        )
    except ClientError as err:
        if err.response['Error']['Code'] == 'TransactionCanceledException':
            reasons = err.response['CancellationReasons']
            if reasons[1]['Code'] == 'ConditionalCheckFailed':
                return {
                    'statusCode': 400,
                    'body': f'Relation between {image_id} and {tag_id} already exists'
                } 
            
            # transaction failed for unknown reason
            print('ERROR: Add relation transaction cancelled.')
            print('Reasons:', reasons)
            return {
                'statusCode': 500,
                'body': 'Transaction was cancelled'
            } 
        else:
            print('ERROR: Unexpected error when adding relation:', str(err))
            return {
                'statusCode': 500,
                'body': json.dumps('Unexpected error while putting image-tag relation in db')
            }    
    
    # success
    return {
        'statusCode': 200,
        'body': json.dumps('New image-tag relation created successfully')
    }

def validate_item_exists(id):
    key = {
        'primary_id': id,
        'secondary_id': id
    }

    response = table.get_item(
        Key=key,
        ProjectionExpression='primary_id'
    )

    if not 'Item' in response:
        raise Exception(f"Item with id {id} does not exist")


