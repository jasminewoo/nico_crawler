from threading import Timer


# code taken from:
# https://stackoverflow.com/questions/2398661/schedule-a-repeating-event-in-python-3

class RepeatedTimer(object):
    def __init__(self, function, *args, **kwargs):
        self._timer = None
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self._setup_timer()

    def _run(self):
        self.function(*self.args, **self.kwargs)
        self._setup_timer()

    def _setup_timer(self):
        self._timer = Timer(1, self._run)
        self._timer.start()

    def stop(self):
        self._timer.cancel()
