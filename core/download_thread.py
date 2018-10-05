from __future__ import unicode_literals

import logging
import time
from threading import Thread
from urllib.error import URLError

import youtube_dl
from youtube_dl.utils import ExtractorError, DownloadError

from core import global_config

logging.getLogger('youtube_dl').setLevel('CRITICAL')
logging.getLogger('urllib').setLevel('CRITICAL')

log = logging.getLogger(__name__)


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
                    success = video.download()
                except RetriableError:
                    success = False
                if success:
                    self.queue.mark_as_done(video)
                    log.info('Finished:      {}'.format(video))
                else:
                    self.queue.enqueue_again(video)
                    log.info('Pending retry: {}'.format(video))
            else:
                if not self.is_daemon:
                    log.debug('This thread is out of work. Existing now...')
                    break
        time.sleep(1)

    def download(self, video):
        if not video.video_id:
            raise AssertionError('self.video_id must be provided')

        is_successful = False

        ydl = youtube_dl.YoutubeDL(get_ydl_options())
        try:
            ret_code = ydl.download([video.url])
        except (URLError, ExtractorError, DownloadError) as e:
            log.debug(e)
            raise RetriableError

        if ret_code == 0:
            if self.storage:
                pass
                # TODO google drive here
            is_successful = True

        return is_successful


class SilentLogger(object):
    def debug(self, msg):
        log.debug(msg)

    def warning(self, msg):
        log.debug(msg)

    def error(self, msg):
        log.debug(msg)


def get_ydl_options():
    return {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloads/%(title)s-%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': global_config.instance['convert_to'],
            'preferredquality': '320',
        }],
        'logger': SilentLogger()
    }


class RetriableError(Exception):
    pass
