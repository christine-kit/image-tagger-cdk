import json
import boto3
import os

table_name = os.environ["TABLE_NAME"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)
from boto3.dynamodb.conditions import Key

"""
Input: http GET request with query parameter tags
example: api/queryImagesByTag?tags=cat&tags=dog

Response:
json object containing list of ids matching the provided tags
"""

def lambda_handler(event, context):
    tags = event.get('queryStringParameters', {}).get('tags', '').split(',')
    item_sets = []
    for tag_id in tags:
        response = table.query(
            KeyConditionExpression=Key('secondary_id').eq(tag_id),
            ProjectionExpression="primary_id",
            IndexName='secondary_id_index'
        )
        item_sets.append(items_to_set(response['Items'], tags))
    items = []
    if item_sets:
        items = set.intersection(*item_sets)

    return {
        'statusCode': 200,
        'body': json.dumps(list(items))
    }

def items_to_set(items, tags):
    return {item['primary_id'] for item in items if not item['primary_id'] in tags}
