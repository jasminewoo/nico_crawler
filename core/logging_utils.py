import logging


class ClosingStreamHandler(logging.StreamHandler):
    def close(self):
        self.flush()
        super().close()


def get_file_log_handler():
    handler = logging.FileHandler('default.log')
    fh_fmt = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(threadName)s %(message)s")
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
