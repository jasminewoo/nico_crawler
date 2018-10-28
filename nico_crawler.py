import logging
import sys
import traceback

from core.app import AppSingleMode, AppDaemonMode
from core.logging_utils import config_logging
from core.notification.gmail import Gmail

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
        log.exception(e)
        Gmail().send('App crash', traceback.format_exc())
