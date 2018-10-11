from indexer.indexer_service import Indexer
import boto3

import logging

log = logging.getLogger(__name__)


class DynamoDbIndexer(Indexer):
    def __init__(self, config=None):
        Indexer.__init__(self, config=config)
        session = boto3.resource('dynamodb')
        self.table = session.Table('nico_crawler')

    def _get_item(self, video_id):
        response = self.table.get_item(
            Key={
                'video_id': video_id
            }
        )
        return response['Item']

    def get_status(self, video_id):
        item = self._get_item(video_id=video_id)
        if item:
            # If the item is there, then it's done.
            return self.k_STATUS_DONE
        else:
            return self.k_STATUS_NOT_FOUND

    def set_status(self, video_id, status):
        item = self._get_item(video_id=video_id)
        if not item:
            if status == self.k_STATUS_DONE:
                self.table.put_item(
                    Item={
                        'video_id': video_id
                    }
                )
            else:
                log.debug('status {} is not supported'.format(status))
        else:
            # TODO: use self.table.update_item()
            pass
