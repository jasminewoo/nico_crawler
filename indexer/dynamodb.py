from datetime import datetime, tzinfo, timedelta

from boto3.dynamodb.conditions import Key

from indexer.indexer_service import Indexer
import boto3

import logging

logging.getLogger('boto').setLevel('CRITICAL')
logging.getLogger('boto3').setLevel('CRITICAL')
logging.getLogger('botocore').setLevel('CRITICAL')
log = logging.getLogger(__name__)

k_VIDEO_ID = 'video_id'
k_VIDEO_STATUS = 'video_status'
k_LAST_MODIFIED_UTC = 'last_modified_utc'


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

    def get_video_ids_by_status(self, status, max_result_set_size=None):
        items = self._get_items_by_status(status, max_result_set_size=max_result_set_size)
        return list(map(lambda x: x[k_VIDEO_ID], items))

    def _get_items_by_status(self, status, max_result_set_size=None):
        response = self.table.query(
            IndexName='video_status-index',
            KeyConditionExpression=Key(k_VIDEO_STATUS).eq(status)
        )

        if 'Items' in response:
            if not max_result_set_size or max_result_set_size > len(response['Items']):
                return response['Items']
            else:
                return response['Items'][:max_result_set_size]
        else:
            return []

    def get_status(self, video_id):
        item = self._get_item(video_id=video_id)
        return item[k_VIDEO_STATUS] if item else self.k_STATUS_NOT_FOUND

    def set_status(self, video_id, status):
        self._update_by_video_id(video_id=video_id, key=k_VIDEO_STATUS, value=status)

    def _get_item(self, video_id):
        response = self.table.get_item(
            Key={
                k_VIDEO_ID: video_id
            }
        )
        return response['Item'] if 'Item' in response else None

    def _update_by_video_id(self, video_id, key, value):
        self.table.update_item(
            Key={
                k_VIDEO_ID: video_id
            },
            UpdateExpression="set {}=:m, {}=:v".format(k_LAST_MODIFIED_UTC, key),
            ExpressionAttributeValues={
                ':v': value,
                ':m': utcnow_in_string()
            },
            ReturnValues="UPDATED_NEW"
        )

    def get_all_video_ids_as_set(self):
        response = self.table.scan()
        if 'Items' in response:
            items = response['Items']
            return set(map(lambda x: x[k_VIDEO_ID], items))
        else:
            return set()


class SimpleUTC(tzinfo):
    def tzname(self, **kwargs):
        return "UTC"

    def utcoffset(self, dt):
        return timedelta(0)


def utcnow_in_string():
    d = datetime.utcnow()
    d = d.replace(tzinfo=SimpleUTC()).isoformat()
    d = str(d).replace('+00:00', 'Z')
    return d
