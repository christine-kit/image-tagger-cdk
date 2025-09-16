import json
import boto3
import os

table_name = os.environ["TABLE_NAME"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

"""
Input: JSON object of form 
{
    "image_id": string, with the form "hash"
    "tag_id": string, with the form "tagname"
} 

Behavior:
inserts an entry into the db with primary_id = image_id and secondary_id = tag_id
does not need to check if entry already exists because the entry only consists
of primary_id and secondary_id, so no changes will be made if overwritten

Response:
http response with status of request
200 if image-tag addition was successful
400 if input error
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

    try:
        validate_item_exists(image_id)
        validate_item_exists(tag_id)
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps(str(e))
        }  

    tag_image_obj = {
        'primary_id': image_id,
        'secondary_id': tag_id,
        'item_type': 'relation'
    }

    try:
        table.put_item(
            Item=tag_image_obj
        )
    except Exception as err:
        print('Unexpected error while putting item in db:', err)
        return {
            'statusCode': 500,
            'body': json.dumps('Unexpected error while putting image-tag object in db')
        }    
    
    # success
    return {
        'statusCode': 200,
        'body': json.dumps('New image-tag object created successfully')
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


