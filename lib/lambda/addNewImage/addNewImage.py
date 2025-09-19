import json
import boto3
from boto3.dynamodb.conditions import Key
from urllib.parse import urlparse
import hashlib
from datetime import datetime, timezone
import os

table_name = os.environ["TABLE_NAME"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

"""
Input: JSON object of form 
{
    "url": string,
    "image_name": string (optional),
    "description": string (optional),
} 
Behavior:
generates a hash based on the url to use as the id in the db.
hash is meant to prevent multiple of the same request generating multiple entries

Response:
http response with status of request
"""
def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        if not body:
            raise Exception
    except:
        return {
            'statusCode': 400,
            'body': json.dumps('Empty or invalid request body')
        }
    if not 'url' in body or not is_valid_url(body['url']):
        return {
            'statusCode': 400,
            'body': json.dumps('URL missing or invalid')
        }
        
    id = hashlib.sha1(body['url'].encode()).hexdigest()
    created_at = datetime.now(timezone.utc).isoformat(timespec='seconds')

    image_obj = {
        'primary_id': id,
        'secondary_id': id,
        'url': body['url'],
        'image_name': str(body.get('image_name')),
        'description': str(body.get('description')),
        'item_type': 'image',
        'created_at': created_at,
        'tag_count': 0
    }

    try:
        condition = ~Key('primary_id').eq(id) & ~Key('secondary_id').eq(id)
        table.put_item(Item=image_obj, ConditionExpression=condition)
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException as err:
        return {
            'statusCode': 400,
            'body': json.dumps(f'Image with url {body['url']} already exists')
        }
    except Exception as err:
        print('Unexpected error while putting item in db:', err)
        return {
            'statusCode': 500,
            'body': json.dumps('Unexpected error while putting image object in db')
        }

    # success
    return {
        'statusCode': 200,
        'body': json.dumps({
            'image_id':id
        })
    }

def is_valid_url(url):
    try:
        res = urlparse(url)
        return all([res.scheme, res.netloc])
    except:
        return False