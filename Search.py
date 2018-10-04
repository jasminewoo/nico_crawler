# http://www.nicovideo.jp/search/sm7141460+歌ってみた?page=2&sort=m&order=d
import json

import requests

from Video import Video


class Search:
    def __init__(self, url):
        self.url = url

    @property
    def videos(self):

        # TODO: what if there are multiple pages?

        r = requests.get(self.url)
        lines = str(r.text).split('\n')
        my_json = None
        for line in lines:
            line = line.strip()
            # TODO: identify video_id's in this search result.

        if not my_json:
            raise RuntimeError('Could not get data from {}'.format(self.url))

        vids = []
        for item in my_json:
            v = Video(info=item['item_data'])
            vids.append(v)

        return vids
