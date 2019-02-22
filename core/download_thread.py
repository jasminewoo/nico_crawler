from __future__ import unicode_literals

import logging
import threading
import time
import traceback
from threading import Thread

from core import config, custom_youtube_dl
from core.utils import logging_utils, string_utils
from core.custom_youtube_dl import RetriableError, LogInError
from core.html_handler.nico_html_parser import ServiceUnderMaintenanceError
from core.model.factory import Factory
from core.model.video import Video
from core.notification.gmail import Gmail

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
                Gmail().send(subject='nico_crawler failure ' + threading.current_thread().getName(),
                             body=traceback.format_exc())
                keep_running = False

    def run_single_iteration(self):
        video = self.queue.peek_and_reserve()
        if video:
            self.logger.debug('Start          {}'.format(video))
            try:
                vt = video.video_type
                if vt == Video.k_VIDEO_TYPE_UTATTEMITA:
                    if not _title_contains_banned_keywords(video):
                        self.logger.info('Downloading:   {}'.format(video))
                        custom_youtube_dl.download(video=video, logger=self.logger, storage=self.storage)
                    else:
                        self.logger.debug('Skipped:       {} for containing banned keyword(s)'.format(video))
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
            except RetriableError as e:
                video.login_failed = type(e) is LogInError
                self.queue.enqueue_again(video)
                self.logger.info('Pending retry: {}'.format(video))
        else:
            if not self.is_daemon:
                self.logger.debug('This thread is out of work. Existing now...')
                return False
            time.sleep(1)
        return True

    def enqueue_related_videos(self, video):
        if not self.is_crawl:
            return
        self.logger.debug('Crawling:      {}'.format(video))
        self.logger.debug('{}.video_type={}'.format(video, video.video_type))
        for url in video.related_urls:
            self.logger.debug('Processing url={}'.format(url))
            factory = Factory(url=url, logger=self.logger)
            try:
                related_videos = factory.get_videos(min_mylist=config.global_instance['minimum_mylist'])
            except (ConnectionError, ConnectionResetError):
                raise RetriableError
            self.logger.debug('{} len(related_videos)={}'.format(url, len(related_videos)))
            results = self.queue.enqueue(related_videos)
            self.logger.debug('{}.enqueue_related_videos {}'.format(video, results))
        self.logger.debug('Crawl Done:    {}'.format(video))


def _title_contains_banned_keywords(video):
    return _title_contains_keywords(video, config.global_instance['banned_keywords'])


def _title_contains_keywords(video, keywords):
    if video.title:
        return string_utils.contains_any_of_substrings(video.title, keywords)
    return False
