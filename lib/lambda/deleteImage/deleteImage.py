import json
import boto3
from boto3.dynamodb.conditions import Key
import os

table_name = os.environ["TABLE_NAME"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

"""
Input: api call with id query parameter like below
api/deleteImage?id=7af39c878d4d7c2838e13d34adaa145807ee3744

Behavior:
deletes all image-tag relations associated with image, then deletes image entry.
behavior is idempotent, will not return an error if the image is already deleted or doesn't exist
"""
def lambda_handler(event, context):
    id = event.get('queryStringParameters', {}).get('id', '')

    response = table.query(
        KeyConditionExpression=Key('primary_id').eq(id),
        ProjectionExpression="secondary_id"
    )
    for item in response['Items']:
        key = {
            'primary_id': id,
            'secondary_id': item['secondary_id']
        }
        table.delete_item(Key=key)
    return {
        'statusCode': 200,
        'body': json.dumps('image deleted')
    }
