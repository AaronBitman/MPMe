import time
from threading import Event, Thread

class RepeatedTimer:
    """Repeat `function` every `interval` seconds."""
    def __init__(self, interval, function, *args, **kwargs):
        """ Start the timer and repeat the
            function every "interval" seconds. """
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.start = time.time()
        self.event = Event()
        self.thread = Thread(target=self._target)
        self.thread.start()

    def _target(self):
        while not self.event.wait(self._time):
            self.function(*self.args, **self.kwargs)

    @property
    def _time(self):
        return self.interval - ((time.time() - self.start) % self.interval)

    def stop(self):
        """ Stop the timer. """
        self.event.set()
        try:
            self.thread.join()
        except RuntimeError:
            # Just in case the timer thread is already stopped, let it go.
            pass
