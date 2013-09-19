import gevent
import logging

class Event(object):

    def __init__(self, *args, **kwargs):
        gevent.spawn(self.run, *args, **kwargs)

    def run(self, *args, **kwargs): return

class EventDispatcher(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.handlers = []

    def __iadd__(self, handler):
        self.handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.handlers.remove(handler)
        return self

    def fire(self, *args, **kwargs):
        for handler in self.handlers:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                self.logger.exception(e)
