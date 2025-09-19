import json
import boto3
import os
from boto3.dynamodb.conditions import Key

table_name = os.environ["TABLE_NAME"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

"""
Input: http GET request

Response:
list of tags (JSON) with the form
[
    "primary_id": "tag id",
    ...
]
"""
def lambda_handler(event, context):
    response = table.query(
        KeyConditionExpression=Key('item_type').eq('tag'),
        ProjectionExpression="primary_id",
        IndexName='created_at_index'
    )
    items = response.get('Items', [])
    return {
        'statusCode': 200,
        'body': json.dumps(items)
    }