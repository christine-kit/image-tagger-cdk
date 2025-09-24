import json
import boto3
import os
from botocore.exceptions import ClientError

table_name = os.environ["TABLE_NAME"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)
client = boto3.client('dynamodb')

"""
api/removeTagFromImage?image_id=imageid&tag_id=tagid

Response:
http response indicating whether the deletion was successful or not
action is idempotent, so performing the action on a image-tag relation
that has already been deleted (or does not exist) does not trigger an error
"""
def lambda_handler(event, context):
    params = event.get('queryStringParameters', {})
    image_id = params.get('image_id', '')
    tag_id = params.get('tag_id', '')
    try:
        response = client.transact_write_items(
            TransactItems = [
                # delete relation, fail if relation does not exist
                {
                    'Delete': {
                        'TableName': table_name,
                        'Key': {
                            'primary_id': {'S': image_id},
                            'secondary_id': {'S': tag_id}
                        },
                        'ConditionExpression': 'attribute_exists(primary_id) AND attribute_exists(secondary_id)'
                    }
                },
                # decrement tag count
                {
                    'Update': {
                        'TableName': table_name,
                        'Key': {
                            'primary_id': {'S': image_id},
                            'secondary_id': {'S': image_id}
                        },
                        'UpdateExpression': 'ADD tag_count :inc',
                        'ExpressionAttributeValues': {
                            ':inc': {'N': '-1'}
                        }
                    }
                }
            ]
        )
    except ClientError as err:
        if err.response['Error']['Code'] == 'TransactionCanceledException':
            reasons = err.response['CancellationReasons']
            if reasons[0]['Code'] == 'ConditionalCheckFailed':
                return {
                    'statusCode': 400,
                    'body': f'Relation between {image_id} and {tag_id} does not exist'
                } 
            
            # transaction failed for unknown reason
            print('ERROR: Remove relation transaction cancelled.')
            print('Reasons:', reasons)
            return {
                'statusCode': 500,
                'body': 'Transaction was cancelled'
            } 
        else:
            print('ERROR: Unexpected error when removing relation:', str(err))
            return {
                'statusCode': 500,
                'body': json.dumps('Unexpected error while putting image-tag relation in db')
            } 

    return {
        'statusCode': 200,
        'body': 'relation deleted successfully'
    }
