import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

table_name = os.environ["TABLE_NAME"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

"""
Input: http GET request

Response:
list of images (JSON) with the form
[
    "primary_id": "image id",
    ...
]
"""
def lambda_handler(event, context):
    response = table.query(
        KeyConditionExpression=Key('item_type').eq('image'),
        ProjectionExpression="primary_id",
        FilterExpression=Attr('tag_count').eq(0),
        IndexName='item_type_index'
    )
    items = response.get('Items', [])
    return {
        'statusCode': 200,
        'body': json.dumps(items)
    }