from __future__ import print_function

import io
import logging
import time
from multiprocessing import Lock

from googleapiclient.discovery import build
from googleapiclient.errors import Error, HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload, MediaInMemoryUpload
from httplib2 import Http, HttpLib2Error, ServerNotFoundError
from oauth2client import file, client, tools

from storage.storage_service import StorageService

logging.getLogger("googleapiclient").setLevel(logging.CRITICAL)
logging.getLogger('httplib2').setLevel(logging.CRITICAL)
logging.getLogger('oauth2client').setLevel(logging.CRITICAL)

SCOPES = 'https://www.googleapis.com/auth/drive'

log = logging.getLogger(__name__)


class GoogleDrive(StorageService):
    def __init__(self, config):
        StorageService.__init__(self)
        self.lock = Lock()
        self.service = None
        self.folder_id = None
        if config:
            self.folder_id = config['google_drive_folder_id']
        self.initialize_service()

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
            raise AssertionError("Provide one of 'path' and 'body'")

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
            self.service.files().delete(fileId=key).execute()
        finally:
            self.lock.release()

    def exists(self, key):
        pass

    def initialize_service(self):
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        trials_remaining = 100
        while trials_remaining > 0:
            trials_remaining -= 1
            try:
                self.service = build('drive', 'v3', http=creds.authorize(Http()))
            except ServerNotFoundError:
                # This may happen when the computer loses internet connection
                log.debug('Initialization failed. trials_remaining={}'.format(trials_remaining))
                time.sleep(2)

    def run_with_retry(self, function, *args, **kwargs):
        trials_remaining = 100
        while trials_remaining > 0:
            trials_remaining -= 1
            try:
                return function(*args, **kwargs)
            except HttpError as e:
                if 'File not found' in e.error_details:
                    raise
                else:
                    log.debug(e)
            except (BrokenPipeError, Error, TimeoutError, HttpLib2Error) as e:
                log.debug(e)

            log.debug('Function call failed. trails_remaining={}'.format(trials_remaining))
            time.sleep(1)
            self.initialize_service()
