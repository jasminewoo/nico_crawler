import json

import requests

from core.video import Video


class MyList:
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
            if line.startswith('Mylist.preload'):
                idx_start = line.find('[')
                line = line[idx_start:-2]
                my_json = json.loads(line)

        if not my_json:
            raise RuntimeError('Could not get data from {}'.format(self.url))

        vids = []
        for item in my_json:
            v = Video(info=item['item_data'])
            vids.append(v)

        return vids
