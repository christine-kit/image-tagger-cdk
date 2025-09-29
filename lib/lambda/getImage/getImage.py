import json
import boto3
import os
from decimal import Decimal

table_name = os.environ["TABLE_NAME"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

"""
Input: http GET request with query parameter id
example: api/getImage?id=595c3cce2409a55c13076f1bac5edee529fc2e58

Response:
json object containing image data
{
    'primary_id': string,
    'secondary_id': string,
    'url': string,
    'image_name': string,
    'description': string,
    'tag_count': int,
    'created_at': string, (UTC ISO format yyyy-mm-ddThh:mm:ss+|–hh:mm)
}
"""
def lambda_handler(event, context):
    ids = event.get('queryStringParameters', {}).get('id', '').split(',')
    imageData = []
    for id in ids:
        key = {
            'primary_id': id,
            'secondary_id': id
        }
        response = table.get_item(
            Key=key
        )
        if 'Item' in response:
            imageData.append(response['Item'])
    
    return {
        'statusCode': 200,
        'body': json.dumps(imageData, cls=DecimalEncoder)
    }

# encode number as int for tag_count attribute
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return json.JSONEncoder.default(self, obj)