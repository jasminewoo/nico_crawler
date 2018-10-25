import logging
from abc import abstractmethod
from html.parser import HTMLParser
from html import unescape

import requests

logging.getLogger('urllib3').setLevel('CRITICAL')


class NicoHTMLParser(HTMLParser):
    def __init__(self, url=None, html_string=None):
        HTMLParser.__init__(self)
        self.status_code = 0

        self.html_vars = self.create_html_vars()

        if url:
            r = requests.get(url)
            self.status_code = r.status_code
            self.html_string = str(r.text)

            unescaped = unescape(self.html_string)

            if self.status_code == 503 or 'ただいまメンテナンス中です' in unescaped or 'Currently under maintenance' in unescaped:
                raise ServiceUnderMaintenanceError

        elif html_string:
            self.html_string = html_string
        else:
            raise AssertionError('No info provided')

        self.feed(self.html_string)
        self.close()

        for html_var in self.html_vars.values():
            if html_var.data:
                html_var.postprocess()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for html_var in self.html_vars.values():
            html_var.process_start_tag(tag, attrs)

    def handle_endtag(self, tag):
        for html_var in self.html_vars.values():
            html_var.process_end_tag(tag)

    def handle_data(self, data):
        for html_var in self.html_vars.values():
            html_var.process_data(data)
        return

    def error(self, message):
        raise RuntimeError(message)

    @abstractmethod
    def create_html_vars(self):
        pass

    @abstractmethod
    def is_available(self):
        pass


class ServiceUnderMaintenanceError(Exception):
    pass
