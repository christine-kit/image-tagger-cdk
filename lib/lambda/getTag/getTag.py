import json
import boto3
import os

table_name = os.environ["TABLE_NAME"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

"""
Input: http GET request with query parameter id
example: api/getTag?id=tagid


Response:
json object containing tag data
"""

def lambda_handler(event, context):
    id = event.get('queryStringParameters', {}).get('id', '')
    key = {
        'primary_id': id,
        'secondary_id': id
    }

    response = table.get_item(
        Key=key
    )

    if not 'Item' in response:
        return {
            'statusCode': 400,
            'body': json.dumps(f'Tag with id {id} does not exist')
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps(response['Item'])
    }
    
