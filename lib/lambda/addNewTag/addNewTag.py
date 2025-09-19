import json
import boto3
from boto3.dynamodb.conditions import Key
from urllib.parse import urlparse
import os
from datetime import datetime, timezone

TAG_TYPES = ['general', 'character', 'source', "artist"]

table_name = os.environ["TABLE_NAME"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)
"""
Input: JSON object of form 
{
    "tag_name": string,
    "description": string (optional),
    "tag_type": string (enum),
    "links": [string] (optional), for artist tags
} 

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
            'body': json.dumps('Empty request body')
        }
    if not 'tag_name' in body:
        return {
            'statusCode': 400,
            'body': json.dumps('request must include tag_name')
        }
    if body.get('tag_type') not in TAG_TYPES:
        return {
            'statusCode': 400,
            'body': json.dumps(f'invalid tag_type, must be one of {TAG_TYPES}')
        }
    tag_name = body['tag_name'].lower()
    
    id = ''.join(tag_name.split())
    created_at = datetime.now(timezone.utc).isoformat(timespec='seconds')

    tag_obj = {
        'tag_name': tag_name,
        'primary_id': id,
        'secondary_id': id,
        'tag_type': body['tag_type'],
        'description': body.get('description', ''),
        'item_type': 'tag',
        'created_at': created_at
    }

    if tag_obj['tag_type'] == 'artist':
        tag_obj['links'] = body.get('links', [])
        if not type(tag_obj['links']) is list:
            return {
                'statusCode': 400,
                'body': json.dumps('links should be list')
            }
        for link in tag_obj['links']:
            if not is_valid_url(link):
                return {
                    'statusCode': 400,
                    'body': json.dumps(f'Invalid url in links: {link}')
                }

    try:
        condition = ~Key('primary_id').eq(id) & ~Key('secondary_id').eq(id)
        table.put_item(Item=tag_obj, ConditionExpression=condition)
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException as err:
        return {
            'statusCode': 400,
            'body': json.dumps(f'Tag with name {tag_obj['tag_name']} already exists')
        }
    except Exception as err:
        print('Unexpected error while putting item in db:', err)
        return {
            'statusCode': 500,
            'body': json.dumps('Unexpected error while putting tag in db')
        }
    
    # success
    print('new tag created and added to db:', tag_obj)
    return {
        'statusCode': 200,
        'body': json.dumps(f'New tag {tag_obj['tag_name']} created successfully.')
    }

def is_valid_url(url):
    try:
        res = urlparse(url)
        return all([res.scheme, res.netloc])
    except:
        return False
