import json
import requests

from Video import Video

if __name__ == '__main__':
    mylist_url = 'http://www.nicovideo.jp/mylist/48382005'
    r = requests.get(mylist_url)
    lines = str(r.text).split('\n')
    my_json = None
    for line in lines:
        line = line.strip()
        if line.startswith('Mylist.preload'):
            idx_start = line.find('[')
            line = line[idx_start:-2]
            with open('mylist.json', 'w') as f:
                my_json = json.loads(line)
                json.dump(my_json, f)

    if not my_json:
        raise RuntimeError('Could not get data from {}'.format(mylist_url))

    for item in my_json:
        v = Video(item['item_data'])
