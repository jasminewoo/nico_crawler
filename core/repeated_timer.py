from threading import Timer


# code taken from:
# https://stackoverflow.com/questions/2398661/schedule-a-repeating-event-in-python-3

class RepeatedTimer(object):
    def __init__(self, interval_in_seconds, function, *args, **kwargs):
        self._timer = None
        self.interval_in_seconds = interval_in_seconds
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self._setup_timer()
        self.need_to_stop = False

    def _run(self):
        self.function(*self.args, **self.kwargs)
        if not self.need_to_stop:
            self._setup_timer()

    def _setup_timer(self):
        if self._timer:
            interval = self.interval_in_seconds
        else:
            # No delay for the very first run
            interval = 0
        self._timer = Timer(interval, self._run)
        self._timer.start()

    def stop(self):
        self.need_to_stop = True
