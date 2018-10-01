from nicotools.download import VideoDmc, VideoSmile, Comment, Thumbnail

import requests

import global_config


class Video:
    def __init__(self, url=None, js=None):
        self.video_id = None
        self.title = ''

        if js:
            self._js = js
            self.video_id = js['video_id']
            self.title = js['title']
            self.is_available = js['deleted'] == '0'
        else:
            # TODO: parse the url and assign value to self.video_id
            pass

    def download(self):
        if not self.video_id:
            raise AssertionError('self.video_id must be provided')

        mail = global_config.instance['email']
        password = global_config.instance['password']

        video_ids = [self.video_id]
        DIR_PATH = global_config.instance['download_location']

        if video_ids[0].startswith('sm'):
            VideoSmile(mail, password).start(video_ids, DIR_PATH)
        else:
            VideoDmc(mail, password).start(video_ids, DIR_PATH)
