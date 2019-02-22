from core.html_handler.nico_html_parser import NicoHTMLParser
from core.html_handler.video_html_variables import *


class VideoHTMLParser(NicoHTMLParser):
    def create_html_vars(self):
        return {
            'title': Title(),
            'tags': Tags(),
            'mylist': MylistCount(),
            'msg': Message(),
            'json': VideoJson(),
            'desc': Description(),
            'login_form': LoginForm()
        }

    @property
    def is_available(self):
        unavailable = self.status_code == 403 or \
                      self.status_code == 404 or \
                      self.html_vars['login_form'].is_present or \
                      self.html_vars['msg'].is_private_or_deleted
        return not unavailable

    @property
    def video_json(self):
        return self.html_vars['json'].data

    @property
    def description(self):
        if not self.is_available:
            return ''
        return self.video_json['video']['description'] if self.video_json else self.html_vars['desc'].data

    @property
    def tags(self):
        if not self.is_available:
            return []
        if self.video_json:
            return list(map(lambda x: x['name'], self.video_json['tags']))
        else:
            return self.html_vars['tags'].data

    @property
    def mylist_count(self):
        if not self.is_available:
            return 0
        if self.video_json:
            return int(self.video_json['video']['mylistCount'])
        else:
            return self.html_vars['mylist'].data

    @property
    def video_title(self):
        if self.video_json:
            return unescape(self.video_json['video']['originalTitle'])
        return None
