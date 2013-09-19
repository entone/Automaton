from automaton import settings
from automaton import util
from automaton.util.event import EventDispatcher
import logging

class Sensor(EventDispatcher):
    display = ""
    change = 5
    value = 0
    type=""
    decorator=""
    id = ""

    def __init__(self, display, interface, events=None, change=5, updaters=None, typ=None):
        super(Sensor, self).__init__()
        self.display = display
        self.id = util.slugify(self.display)
        self.interface = interface
        self.change = change
        self.handlers = events if events else []
        self.updaters = updaters
        if typ: self.type = typ
        self.logger = logging.getLogger(__name__)

    def do_conversion(self, value):
        self.value = self.conversion(value)
        if self.updaters: self.do_update()
        return self.value

    def do_update(self):
        for i in self.updaters:
            try:
                i(self.value)
            except Exception as e:
                self.logger.warning(e)

    def conversion(self, value):
        return value

    def get_value(self):
        return self.value

    def json(self):
        return dict(
            id=self.id,
            display=self.display,
            type=self.type,
            value=self.value,
            change=self.change,
            decorator=self.decorator,
            cls=self.__class__.__name__
        )