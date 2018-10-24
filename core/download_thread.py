from __future__ import unicode_literals

import logging
import time
from threading import Thread
from urllib.error import URLError

from youtube_dl.utils import ExtractorError, DownloadError

from core import global_config
from core.custom_youtube_dl import CustomYoutubeDL
from core.nico_object_factory import NicoObjectFactory
from core.video import Video

logging.getLogger('youtube_dl').setLevel('CRITICAL')
logging.getLogger('urllib').setLevel('CRITICAL')

log = logging.getLogger(__name__)


class DownloadThread(Thread):
    def __init__(self, queue, storage=None, is_daemon=False, is_crawl=False):
        Thread.__init__(self)
        self.queue = queue
        self.storage = storage
        self.is_daemon = is_daemon
        self.is_crawl = is_crawl

    def run(self):
        while True:
            video = self.queue.peek_and_reserve()
            if video:
                log.info('Start          {}'.format(video))
                try:
                    vt = video.video_type
                    if vt == Video.k_VIDEO_TYPE_UTATTEMITA:
                        log.info('Downloading:   {}'.format(video))
                        self.download(video=video)
                        self.queue.mark_as_done(video)
                        log.info('Finished:      {}'.format(video))
                        self.enqueue_related_videos(video=video)
                    else:
                        self.enqueue_related_videos(video=video)
                        self.queue.mark_as_referenced(video)
                        log.info('Referenced:    {}'.format(video))
                except RetriableError:
                    self.queue.enqueue_again(video)
                    log.info('Pending retry: {}'.format(video))
                except LogInError:
                    self.queue.mark_as_login_required(video)
                    log.info('LogInError:    {}'.format(video))
            else:
                if not self.is_daemon:
                    log.debug('This thread is out of work. Existing now...')
                    break
                time.sleep(1)

    def download(self, video):
        ydl = CustomYoutubeDL(video)
        try:
            if ydl.download() != 0:
                raise RuntimeError
            if self.storage:
                self.storage.upload_file(ydl.filename, ydl.path)
        except (URLError, ExtractorError, DownloadError) as e:
            if 'Niconico videos now require logging in' in str(e):
                raise LogInError
            else:
                log.debug(e)
                raise RetriableError
        if self.storage:
            ydl.remove_local_file()

    def enqueue_related_videos(self, video):
        if not self.is_crawl:
            return
        log.info('Crawling:      {}'.format(video))
        for url in video.get_related_urls():
            log.debug('Processing url={}'.format(url))
            related_videos = NicoObjectFactory(url=url).get_videos(min_mylist=global_config.instance['minimum_mylist'])
            log.debug('{} len(related_videos)={}'.format(url, len(related_videos)))
            for rv in related_videos:
                self.queue.enqueue(video=rv, parent_video=video)
        log.info('Crawl Done:    {}'.format(video))


class RetriableError(Exception):
    pass


class LogInError(Exception):
    pass
