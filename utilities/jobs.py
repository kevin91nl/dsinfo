import functools
import threading
from multiprocessing import Process


class SignalJob(threading.Thread):

    def __init__(self, target, args, kwargs):
        super().__init__()
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.signal = True

    def stop(self):
        self.signal = False

    def run(self):
        # Repeatable job
        while self.signal:
            self.target.__call__(*self.args, **self.kwargs)


class StreamingJob:

    def __init__(self, target):
        super().__init__()
        self.target = target
        self.signal = True

    def stop(self):
        self.target.terminate()
        self.signal = False

    def start(self):
        self.target.start()

    def is_alive(self):
        return self.signal
