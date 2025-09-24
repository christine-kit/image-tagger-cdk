import json
import boto3
import os
from boto3.dynamodb.conditions import Key

table_name = os.environ["TABLE_NAME"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

"""
Periodic job that updates untagged image count to be consistent with the number of
image entries with tag_count = 0

Assumes consistency with tag_count being equal to the number of tags each image has,
which is enforced atomically whenever image-tag relations are added/removed
"""

def lambda_handler(event, context):
    print('Running periodic untagged_count repair job')
    # fetch all image items
    query_response = table.query(
        KeyConditionExpression=Key('item_type').eq('image'),
        ProjectionExpression='tag_count',
        IndexName='item_type_index'
    )
    # get current untagged count
    count_response = table.get_item(
        Key = {
            'primary_id': 'UNTAGGED_COUNT',
            'secondary_id': 'UNTAGGED_COUNT'
        },
        ProjectionExpression='untagged_count'
    )
    count_item = count_response.get('Item', None)
    current_count = count_item.get('untagged_count', None) if count_item else None

    count = 0
    for item in query_response['Items']:
        if item['tag_count'] == 0:
            count += 1
    
    if count != current_count:
        # log inconsistency for debug purposes
        print('Untagged image count drift detected:')
        print(f'Current untagged count: {current_count}')
        print(f'New untagged count: {count}')

    # create new count item and add to db
    new_count_item = {
        'primary_id': 'UNTAGGED_COUNT',
        'secondary_id': 'UNTAGGED_COUNT',
        'item_type': 'metadata',
        'untagged_count': count
    }
    table.put_item(Item=new_count_item)