import sys


class DelayedException(object):
    # Taken from http://stackoverflow.com/questions/6126007 ...
    # /python-getting-a-traceback-from-a-multiprocessing-process
    def __init__(self, exc):
        self.exc = exc
        _, _, self.traceback = sys.exc_info()

    def re_raise(self):
        raise self.exc, None, self.traceback
