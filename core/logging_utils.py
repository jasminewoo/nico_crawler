import logging
import os

k_LOGS_FOLDER = 'logs'


class ClosingStreamHandler(logging.StreamHandler):
    def close(self):
        self.flush()
        super().close()


def get_file_log_handler(name='default'):
    if not os.path.exists(k_LOGS_FOLDER):
        os.mkdir(k_LOGS_FOLDER)
    handler = logging.FileHandler('{}/{}.log'.format(k_LOGS_FOLDER, name))
    fh_fmt = logging.Formatter("%(asctime)s %(levelname)8s %(threadName)9s %(funcName)s %(message)s")
    fh_fmt.datefmt = '%Y-%m-%d %H:%M:%S'
    handler.setFormatter(fh_fmt)
    handler.setLevel(logging.DEBUG)
    return handler


def get_console_log_handler():
    handler = ClosingStreamHandler()
    handler.setLevel(logging.INFO)
    return handler


def config_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(get_console_log_handler())
    root.addHandler(get_file_log_handler())


def add_file_handler(logger, thread):
    name = thread.getName().split('-')[1] + '-Thread'
    new_handler = get_file_log_handler(name)
    logger.addHandler(new_handler)
