import json
import boto3
import os

table_name = os.environ["TABLE_NAME"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)
from boto3.dynamodb.conditions import Key

"""
Input: http GET request with query parameter id
example: api/queryTagsByImage?id=595c3cce2409a55c13076f1bac5edee529fc2e58

Response:
json object containing list of tag ids
"""
def lambda_handler(event, context):
    id = event.get('queryStringParameters', {}).get('id', '')
    try:
        response = table.query(
            KeyConditionExpression=Key('primary_id').eq(id),
            ProjectionExpression="secondary_id, item_type"
        )
    except Exception as err:
        print('Unexpected error while querying db:', err)
        return {
            'statusCode': 500,
            'body': json.dumps('Unexpected error while querying by image')
        }
    
    items = response.get('Items', [])
    
    if not items:
        return {
            'statusCode': 400,
            'body': json.dumps(f'image with id {id} does not exist')
        }
    items = [item.get('secondary_id', '') for item in items
        if item.get('item_type', '') == 'relation']

    return {
        'statusCode': 200,
        'body': json.dumps(items)
    }
