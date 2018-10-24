from __future__ import unicode_literals

import logging
import threading
import time
from threading import Thread
from urllib.error import URLError

from youtube_dl.utils import ExtractorError, DownloadError

from core import global_config, logging_utils
from core.custom_youtube_dl import CustomYoutubeDL
from core.nico_object_factory import NicoObjectFactory
from core.video import Video

logging.getLogger('urllib').setLevel('CRITICAL')


class DownloadThread(Thread):
    def __init__(self, queue, storage=None, is_daemon=False, is_crawl=False):
        Thread.__init__(self)
        self.logger = None
        self.queue = queue
        self.storage = storage
        self.is_daemon = is_daemon
        self.is_crawl = is_crawl

    def run(self):
        self.logger = logging.getLogger(str(threading.get_ident()))
        logging_utils.add_file_handler(logger=self.logger, thread=threading.current_thread())

        keep_running = True
        while keep_running:
            try:
                keep_running = self.run_single_iteration()
            except Exception as e:
                self.logger.error(e)
                keep_running = False

    def run_single_iteration(self):
        video = self.queue.peek_and_reserve()
        if video:
            self.logger.info('Start          {}'.format(video))
            try:
                vt = video.video_type
                if vt == Video.k_VIDEO_TYPE_UTATTEMITA:
                    self.logger.info('Downloading:   {}'.format(video))
                    self.download(video=video)
                    self.queue.mark_as_done(video)
                    self.logger.info('Finished:      {}'.format(video))
                    self.enqueue_related_videos(video=video)
                else:
                    self.enqueue_related_videos(video=video)
                    self.queue.mark_as_referenced(video)
                    self.logger.info('Referenced:    {}'.format(video))
            except RetriableError:
                self.queue.enqueue_again(video)
                self.logger.info('Pending retry: {}'.format(video))
            except LogInError:
                self.queue.mark_as_login_required(video)
                self.logger.info('LogInError:    {}'.format(video))
        else:
            if not self.is_daemon:
                self.logger.debug('This thread is out of work. Existing now...')
                return False
            time.sleep(1)
        return True

    def download(self, video):
        ydl = CustomYoutubeDL(video, logger=self.logger)
        try:
            if ydl.download() != 0:
                raise RuntimeError
            if self.storage:
                self.storage.upload_file(ydl.filename, ydl.path)
        except (URLError, ExtractorError, DownloadError) as e:
            if 'Niconico videos now require logging in' in str(e):
                raise LogInError
            else:
                self.logger.debug(e)
                raise RetriableError
        if self.storage:
            ydl.remove_local_file()

    def enqueue_related_videos(self, video):
        if not self.is_crawl:
            return
        self.logger.info('Crawling:      {}'.format(video))
        for url in video.get_related_urls(logger=self.logger):
            self.logger.debug('Processing url={}'.format(url))
            related_videos = NicoObjectFactory(url=url, logger=self.logger).get_videos(
                min_mylist=global_config.instance['minimum_mylist'])
            self.logger.debug('{} len(related_videos)={}'.format(url, len(related_videos)))
            for rv in related_videos:
                self.queue.enqueue(video=rv, parent_video=video, logger=self.logger)
        self.logger.info('Crawl Done:    {}'.format(video))


class RetriableError(Exception):
    pass


class LogInError(Exception):
    pass
