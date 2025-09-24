import json
import boto3
import os

table_name = os.environ["TABLE_NAME"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

"""
Input: http GET request
example: api/getUntaggedCount


Response:
number of untagged image items
count is eventually consistent, updated once every day
"""

def lambda_handler(event, context):
    key = {
        'primary_id': 'UNTAGGED_COUNT',
        'secondary_id': 'UNTAGGED_COUNT'
    }
    response = table.get_item(
        Key=key
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps(int(response['Item']['untagged_count']))
    }
    
