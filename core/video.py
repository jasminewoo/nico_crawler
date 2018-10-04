import logging

log = logging.getLogger(__name__)


class Video:
    def __init__(self, video_id=None, url=None, info=None):
        self.title = None
        if url:
            self.video_id = url.split('/')[-1]
        if info:
            self._js = info
            self.video_id = info['video_id']
            self.title = info['title']
            self.is_available = info['deleted'] == '0'
        if video_id:
            self.video_id = video_id

    def __str__(self):
        return '{} {}'.format(self.title, self.video_id) if self.title else self.video_id

    def download(self, convert_to=None):
        if not self.is_available:
            log.info('Skip: the video was deleted {}'.format(self))
        if not self.video_id:
            raise AssertionError('self.video_id must be provided')

        # TODO: download video

        if convert_to:
            # TODO: convert to the specified ext
            # TODO: delete original file (ie. mp4)
            pass
