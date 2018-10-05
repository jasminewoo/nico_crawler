import logging
import sys

from core.app import App, AppSingleMode, AppDaemonMode
from core.logging_utils import config_logging

log = logging.getLogger(__name__)

if __name__ == '__main__':
    config_logging()

    if len(sys.argv) > 1:
        AppSingleMode(url=sys.argv[1])
    else:
        AppDaemonMode()
        log.info('Ready to process requests')

    log.info('Exiting...')
