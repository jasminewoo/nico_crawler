import logging
import sys

from core.app import App
from core.logging_utils import config_logging

log = logging.getLogger(__name__)

if __name__ == '__main__':

    if len(sys.argv) < 1:
        raise AssertionError('Please provide a URL')

    config_logging()

    app = App()
    app.process(url=sys.argv[1])
