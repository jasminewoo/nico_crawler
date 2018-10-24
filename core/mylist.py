import json

import requests

from core.video import Video


class MyList:
    def __init__(self, url, logger=None):
        self.url = url
        self.logger = logger

    def __str__(self):
        return '/'.join(self.url.split('/')[-2:])

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

            for item in my_json:
                id = item['item_data']['video_id']
                mlc = int(item['item_data']['mylist_counter'])
                v = Video(video_id=id, mylist_count=mlc)
                vids.append(v)
        elif r.status_code == 403 or r.status_code == 404 or '非公開マイリスト' in html_str:
            self.logger.debug('Private mylist {}'.format(self.url))
        else:
            raise RuntimeError('Could not get data from {}'.format(self.url))

        return vids
