import re

from core.html_handler.video_html_parser import VideoHTMLParser

url_regex_str = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'


class Video:
    k_VIDEO_TYPE_UTATTEMITA = 'utattemita'
    k_VIDEO_TYPE_VOCALOID_ORG = 'org'
    k_VIDEO_TYPE_UNKNOWN = 'unknown'

    def __init__(self, video_id=None, url=None, mylist_count=None):
        if url:
            self.video_id = url.split('/')[-1].split('?')[0]
        if video_id:
            self.video_id = video_id
        self._html = None
        self.requires_creds_to_download = False
        self._mylist_count = mylist_count

    @property
    def related_urls(self):
        urls = []
        vt = self.video_type
        if vt == self.k_VIDEO_TYPE_UTATTEMITA:
            matches = re.findall(url_regex_str, self.html.description)
            for url in matches:
                if 'nicovideo' not in url:
                    continue
                if '/watch/' in url or '/mylist/' in url:
                    urls.append(url)
        elif vt == self.k_VIDEO_TYPE_VOCALOID_ORG:
            search_template = 'https://www.nicovideo.jp/search/{}%20%E6%AD%8C%E3%81%A3%E3%81%A6%E3%81%BF%E3%81%9F'
            urls.append(search_template.format(self.video_id))

        return urls

    @property
    def url(self):
        return 'http://www.nicovideo.jp/watch/' + self.video_id

    @property
    def video_type(self):
        tags = self.html.tags
        if tags is None:
            raise ValueError('{} has no tags; {}'.format(self, self.html.html_string))

        if '歌ってみた' in tags:
            return self.k_VIDEO_TYPE_UTATTEMITA
        elif 'VOCALIOD' in tags or 'Vocaloid' in tags or 'vocaloid' in tags:
            return self.k_VIDEO_TYPE_VOCALOID_ORG
        else:
            return self.k_VIDEO_TYPE_UNKNOWN

    @property
    def mylist_count(self):
        return self._mylist_count if self._mylist_count else self.html.mylist_count

    @property
    def html(self):
        if not self._html:
            self._html = VideoHTMLParser(url=self.url)
        return self._html

    def __str__(self):
        return self.video_id
