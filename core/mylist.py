import json
import logging

import requests

from core.video import Video

log = logging.getLogger(__name__)


class MyList:
    def __init__(self, url):
        self.url = url

    @property
    def videos(self):
        vids = []

        r = requests.get(self.url)
        html_str = str(r.text)

        if r.status_code == 200:

            lines = html_str.split('\n')
            my_json = None
            for line in lines:
                line = line.strip()
                if line.startswith('Mylist.preload'):
                    idx_start = line.find('[')
                    line = line[idx_start:-2]
                    my_json = json.loads(line)

            if not my_json:
                raise RuntimeError('Could not get data from {}'.format(self.url))

            for item in my_json:
                v = Video(video_id=item['item_data']['video_id'])
                vids.append(v)
        elif r.status_code == 403 or r.status_code == 404 or '非公開マイリスト' in html_str:
            log.debug('Private mylist {}'.format(self.url))

        return vids
