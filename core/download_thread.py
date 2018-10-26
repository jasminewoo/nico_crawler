from __future__ import unicode_literals

import logging
import threading
import time
from threading import Thread
from urllib.error import URLError

from youtube_dl.utils import ExtractorError, DownloadError

from core import global_config, logging_utils
from core.custom_youtube_dl import CustomYoutubeDL
from core.html_handler.nico_html_parser import ServiceUnderMaintenanceError
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
                self.logger.exception(e)
                keep_running = False

    def run_single_iteration(self):
        video = self.queue.peek_and_reserve()
        if video:
            self.logger.debug('Start          {}'.format(video))
            try:
                vt = video.video_type
                if vt == Video.k_VIDEO_TYPE_UTATTEMITA:
                    self.logger.info('Downloading:   {}'.format(video))
                    self.download(video=video)
                    self.queue.mark_as_done(video)
                    self.logger.info('Finished:      {}'.format(video))
                    self.enqueue_related_videos(video=video)
                elif vt == Video.k_VIDEO_TYPE_VOCALOID_ORG:
                    self.enqueue_related_videos(video=video)
                    self.queue.mark_as_referenced(video)
                    self.logger.debug('Referenced:    {}'.format(video))
                else:
                    self.queue.mark_as_referenced(video)
                    self.logger.debug('Skipped:       {}'.format(video))
            except ServiceUnderMaintenanceError:
                self.queue.enqueue_again(video)
                self.logger.info('Service under maintenance; thread going to sleep for 30 min...')
                time.sleep(1800)
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
        self.logger.debug('Crawling:      {}'.format(video))
        self.logger.debug('{}.video_type={}'.format(video, video.video_type))
        for url in video.related_urls:
            self.logger.debug('Processing url={}'.format(url))
            factory = NicoObjectFactory(url=url, logger=self.logger)
            related_videos = factory.get_videos(min_mylist=global_config.instance['minimum_mylist'])
            self.logger.debug('{} len(related_videos)={}'.format(url, len(related_videos)))
            results = self.queue.enqueue(related_videos)
            self.logger.debug('{}.enqueue_related_videos {}'.format(video, results))
        self.logger.debug('Crawl Done:    {}'.format(video))


class RetriableError(Exception):
    pass


class LogInError(Exception):
    pass
