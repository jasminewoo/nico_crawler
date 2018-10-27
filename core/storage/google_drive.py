from __future__ import print_function

import io
import logging
import time
from multiprocessing import Lock

from googleapiclient.errors import Error, HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload, MediaInMemoryUpload
from httplib2 import HttpLib2Error

from core import google_utils
from core.storage.storage_service import StorageService

logging.getLogger("googleapiclient").setLevel(logging.CRITICAL)
logging.getLogger('httplib2').setLevel(logging.CRITICAL)
logging.getLogger('oauth2client').setLevel(logging.CRITICAL)

SCOPES = 'https://www.googleapis.com/auth/drive'

log = logging.getLogger(__name__)


class GoogleDrive(StorageService):
    def __init__(self, config=None):
        StorageService.__init__(self)
        log.info('Google Driving initializing...')
        self.lock = Lock()
        self.service = None
        self.folder_id = None
        if config:
            self.folder_id = config['google_drive_folder_id']

    def update_with_file(self, key, path):
        self._upload(is_new_entity=False, key=key, path=path)

    def download_as_file(self, key, dst_path):
        log.debug("Downloading '{}' as {}".format(key, dst_path))
        with open(dst_path, 'wb') as fp:
            self._download(key, fp)
        log.debug("File downloaded as '{}'".format(dst_path))

    def download_as_bytes(self, key):
        with io.BytesIO() as fp:
            self._download(key, fp)
            data = fp.getvalue()
        return data

    def _download(self, key, fp):
        return self.run_with_retry(self._download_inner, key=key, fp=fp)

    def _download_inner(self, key, fp):
        try:
            self.lock.acquire()
            self.initialize_service()
            request = self.service.files().get_media(fileId=key)
            downloader = MediaIoBaseDownload(fp, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
        finally:
            self.lock.release()

    def upload_file(self, name, path):
        return self._upload(name=name, path=path)

    def upload_bytes(self, name, data):
        with io.BytesIO() as fp:
            return self._upload(name=name, fp=fp)

    def update_with_bytes(self, key, data):
        return self._upload(is_new_entity=False, key=key, data=data)

    def _upload(self, is_new_entity=True, key=None, name=None, path=None, data=None):
        return self.run_with_retry(self._upload_inner, is_new_entity=is_new_entity, key=key, name=name,
                                   path=path, data=data)

    def _upload_inner(self, is_new_entity=True, key=None, name=None, path=None, data=None):
        if (1 if path else 0) + (1 if data else 0) != 1:
            raise AssertionError("Provide one of 'path' and 'data'")

        if not is_new_entity and not key:
            raise AssertionError('fileId (aka. key) must be provided when updating an existing entity')

        if is_new_entity and not name:
            raise AssertionError('name must be provided when creating a new entity in Google Drive')

        if path:
            media = MediaFileUpload(path)
        else:
            media = MediaInMemoryUpload(data)

        try:
            self.lock.acquire()
            self.initialize_service()
            if is_new_entity:
                metadata = {'name': name}
                if self.folder_id:
                    metadata['parents'] = [self.folder_id]
                file = self.service.files().create(body=metadata, media_body=media, fields='id').execute()
            else:
                file = self.service.files().update(media_body=media, fileId=key, fields='id').execute()
            return file.get('id')
        finally:
            self.lock.release()

    def delete(self, key):
        return self.run_with_retry(self._delete_inner, key)

    def _delete_inner(self, key):
        try:
            self.lock.acquire()
            self.initialize_service()
            self.service.files().delete(fileId=key).execute()
        finally:
            self.lock.release()

    def create_folder(self, folder_name):
        raise NotImplementedError

    def exists(self, key):
        raise NotImplementedError

    def initialize_service(self):
        if not self.service:
            self.service = google_utils.create_service(api_name='drive', api_version='v3', scopes=SCOPES)

    def run_with_retry(self, function, *args, **kwargs):
        while True:
            try:
                return function(*args, **kwargs)
            except HttpError as e:
                if 'File not found' in e.error_details:
                    raise
                else:
                    log.debug(e)
            except (BrokenPipeError, Error, TimeoutError, HttpLib2Error) as e:
                log.debug(e)

            self.initialize_service()
            time.sleep(2)
