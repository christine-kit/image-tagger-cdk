import json
import boto3
import os
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

table_name = os.environ["TABLE_NAME"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)
client = boto3.client('dynamodb')

"""
Input: api call with tag id query parameter like below
api/deleteTag?id=tagid

Behavior:
atomically deletes all image-tag relations associated with the tag, then deletes the tag
if any deletion fails the transaction is rolled back
"""
def lambda_handler(event, context):
    tag_id = event.get('queryStringParameters', {}).get('id', '')
    # gets all items with secondary_id = tag_id, including the tag item (primary_id = secondary_id = tag_id)
    response = table.query(
        KeyConditionExpression=Key('secondary_id').eq(tag_id),
        ProjectionExpression="primary_id",
        IndexName='secondary_id_index'
    )
    transaction = []
    for item in response['Items']:
        id = item['primary_id']
        # delete relation or item (may include tag item)
        transaction.append({
            'Delete': {
                'TableName': table_name,
                'Key': {
                    'primary_id': {'S': id},
                    'secondary_id': {'S': tag_id}
                },
                'ConditionExpression': 'attribute_exists(primary_id) AND attribute_exists(secondary_id)'
            }
        })
        # decrement tag_count on image by 1 
        # don't decrement if id == tag_id since that represents a tag element
        if id == tag_id:
            continue
        transaction.append({
            'Update': {
                'TableName': table_name,
                'Key': {
                    'primary_id': {'S': id},
                    'secondary_id': {'S': id}
                },
                'UpdateExpression': 'ADD tag_count :inc',
                'ExpressionAttributeValues': {
                    ':inc': {'N': '-1'}
                }
            }
        })
    try:
        client.transact_write_items(TransactItems = transaction)
    except ClientError as err:
        if err.response['Error']['Code'] == 'TransactionCanceledException':
            reasons = err.response['CancellationReasons']
            # transaction failed for unknown reason
            print('ERROR: Remove relation transaction cancelled.')
            print('Reasons:', reasons)
            return {
                'statusCode': 500,
                'body': 'Transaction was cancelled'
            } 
        else:
            print('ERROR: Unexpected error when removing relation:', str(err))
            return {
                'statusCode': 500,
                'body': json.dumps('Unexpected error while putting image-tag relation in db')
            } 
        
    return {
        'statusCode': 200,
        'body': f'Tag {tag_id} deleted successfully. {len(response['Items'])} entries removed.'
    }

    
