import json
import boto3
import os

table_name = os.environ["TABLE_NAME"]
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

"""
api/removeTagFromImage?image_id=imageid&tag_id=tagid

Response:
http response indicating whether the deletion was successful or not
action is idempotent, so performing the action on a image-tag relation
that has already been deleted (or does not exist) does not trigger an error
"""
def lambda_handler(event, context):
    params = event.get('queryStringParameters', {})
    image_id = params.get('image_id', '')
    tag_id = params.get('tag_id', '')
    key = {
        'primary_id': image_id,
        'secondary_id': tag_id
    }
    try:
        response = table.delete_item(Key=key)
        return {
        'statusCode': 200,
        'body': json.dumps(f'removed {tag_id} from image {image_id}')
    }
    except Exception as e:
        print('unexpected error when deleting item with Key: ', key)
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps('unexpected error when deleting image-tag relation')
        }

