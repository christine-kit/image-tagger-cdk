import json
import boto3
from boto3.dynamodb.conditions import Key
import os

table_name = os.environ["TABLE_NAME"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

"""
Input: api call with tag id query parameter like below
api/deleteTag?id=tagid

Behavior:
deletes all image-tag relations associated with the tag, then deletes the tag
"""
def lambda_handler(event, context):
    id = event.get('queryStringParameters', {}).get('id', '')


    response = table.query(
        KeyConditionExpression=Key('secondary_id').eq(id),
        ProjectionExpression="primary_id",
        IndexName='secondary_id_index'
    )
    for item in response['Items']:
        key = {
            'primary_id': item['primary_id'],
            'secondary_id': id
        }
        table.delete_item(Key=key)
    return {
        'statusCode': 200,
        'body': json.dumps('tag deleted')
    }

    
