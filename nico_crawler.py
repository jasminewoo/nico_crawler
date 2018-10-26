import logging
import sys

from core.app import AppSingleMode, AppDaemonMode
from core.logging_utils import config_logging

log = logging.getLogger(__name__)
config_logging()

if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            log.info('AppSingleMode')
            AppSingleMode(url=sys.argv[1])
            log.info('Exiting...')
        else:
            log.info('AppDaemonMode')
            AppDaemonMode()
    except Exception as e:
        log.error(e)
