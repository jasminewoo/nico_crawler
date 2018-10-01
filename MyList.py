import json

import requests

from Video import Video


class MyList:
    def __init__(self, url):
        self.url = url

    @property
    def videos(self):
        r = requests.get(self.url)
        lines = str(r.text).split('\n')
        my_json = None
        for line in lines:
            line = line.strip()
            if line.startswith('Mylist.preload'):
                idx_start = line.find('[')
                line = line[idx_start:-2]
                my_json = json.loads(line)
                # with open('mylist.json', 'w') as f:
                #     json.dump(my_json, f)

        if not my_json:
            raise RuntimeError('Could not get data from {}'.format(self.url))

        for item in my_json:
            v = Video(item['item_data'])
            v.download()
