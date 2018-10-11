from boto3.dynamodb.conditions import Key

from indexer.indexer_service import Indexer
import boto3

import logging

log = logging.getLogger(__name__)


class DynamoDbIndexer(Indexer):
    def __init__(self, config=None):
        Indexer.__init__(self, config=config)
        session = boto3.Session(
            aws_access_key_id=config['aws_access_key_id'],
            aws_secret_access_key=config['aws_secret_access_key'],
            region_name=config['aws_region']
        )
        ddb = session.resource('dynamodb')
        self.table = ddb.Table('nico_crawler')

    def get_pending_video_ids(self):
        video_ids = []

        response = self.table.query(
            IndexName='video_status-index',
            KeyConditionExpression=Key('video_status').eq(self.k_STATUS_PENDING)
        )

        if 'Items' in response:
            for item in response['Items']:
                video_ids.append(item['video_id'])

        return video_ids

    def _get_item(self, video_id):
        response = self.table.get_item(
            Key={
                'video_id': video_id
            }
        )
        return response['Item'] if 'Item' in response else None

    def get_status(self, video_id):
        item = self._get_item(video_id=video_id)
        if item:
            # If the item is there, then it's done.
            return self.k_STATUS_DONE
        else:
            return self.k_STATUS_NOT_FOUND

    def set_status(self, video_id, status):
        self.table.update_item(
            Key={
                'video_id': video_id
            },
            UpdateExpression="set video_status = :s",
            ExpressionAttributeValues={
                ':s': status
            },
            ReturnValues="UPDATED_NEW"
        )

    def _create_table(self):
        # video_status-index
        # read/write capacity 1
        pass
