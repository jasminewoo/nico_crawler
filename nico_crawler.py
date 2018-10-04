import logging
import os

from core.app import App
from core.logging_utils import config_logging

log = logging.getLogger(__name__)

if __name__ == '__main__':
    url = 'http://www.nicovideo.jp/mylist/48382005'

    config_logging()

    app = App()
    app.process(url=url)
