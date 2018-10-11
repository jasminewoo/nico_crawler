from __future__ import unicode_literals

import logging
import os
import time
from threading import Thread
from urllib.error import URLError

import youtube_dl
from youtube_dl.utils import ExtractorError, DownloadError

from core import global_config

logging.getLogger('youtube_dl').setLevel('CRITICAL')
logging.getLogger('urllib').setLevel('CRITICAL')

log = logging.getLogger(__name__)

k_DOWNLOADS_FOLDER_PATH = 'downloads'


class DownloadThread(Thread):
    def __init__(self, queue, storage=None, is_daemon=False):
        Thread.__init__(self)
        self.queue = queue
        self.storage = storage
        self.is_daemon = is_daemon

    def run(self):
        while True:
            video = self.queue.peek_and_reserve()
            if video:
                log.debug('Starting to process {}'.format(video))
                try:
                    self.download(video=video)
                    self.queue.mark_as_done(video)
                    log.info('Finished:      {}'.format(video))
                except RetriableError:
                    self.queue.enqueue_again(video)
                    log.info('Pending retry: {}'.format(video))
                except LogInError:
                    self.queue.mark_as_errored(video)
                    log.info('LogInError:    {}'.format(video))
            else:
                if not self.is_daemon:
                    log.debug('This thread is out of work. Existing now...')
                    break
        time.sleep(1)

    def download(self, video):
        ret_code = -1

        ydl = youtube_dl.YoutubeDL(get_ydl_options())
        try:
            ret_code = ydl.download([video.url])
        except (URLError, ExtractorError, DownloadError) as e:
            log.debug(e)
            if 'Niconico videos now require logging in' in str(e):
                raise LogInError
            raise RetriableError

        filename = get_filename_by_video_id(video_id=video.video_id)
        if filename:
            path = '{}/{}'.format(k_DOWNLOADS_FOLDER_PATH, filename)

        if ret_code == 0:
            if self.storage:
                self.storage.upload_file(filename, path)

        if self.storage and filename:
            os.remove(path)

        if ret_code != 0:
            raise RetriableError


class SilentLogger(object):
    def debug(self, msg):
        log.debug(msg)

    def warning(self, msg):
        log.debug(msg)

    def error(self, msg):
        log.debug(msg)


class RetriableError(Exception):
    pass


class LogInError(Exception):
    pass


def get_ydl_options():
    return {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': '{}/%(upload_date)-s%(title)s-%(id)s.%(ext)s'.format(k_DOWNLOADS_FOLDER_PATH),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': global_config.instance['convert_to'],
            'preferredquality': '320',
        }],
        'logger': SilentLogger()
    }


def get_filename_by_video_id(video_id):
    files = os.listdir(k_DOWNLOADS_FOLDER_PATH)
    filtered_list = list(filter(lambda f: video_id in f, files))
    if filtered_list and len(filtered_list) > 0:
        return filtered_list[0]
    return None
