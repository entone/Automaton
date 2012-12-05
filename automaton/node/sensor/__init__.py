import settings
import util

class Sensor(object):
    index = ""
    display = ""
    id = ""
    change = 2
    data_rate = 64
    current_value = 0
    interface = None
    decorator = ""
    type = ""

    def __init__(self, index, display, interface, change=2, data_rate=64):
        self.index = index
        self.display = display
        self.id = util.slugify(display)
        self.change = change
        self.data_rate = data_rate
        self.interface = interface
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))

    def do_conversion(self, val): 
        self.current_value = self.conversion(float(val))
        return self.current_value

    def get_value(self):
        try:
            val = self.interface.interface_kit.getSensorValue(self.index)
            return self.do_conversion(val)
        except Exception as e:
            self.logger.error("No value for: %s" % self.__class__.__name__)

        return None

    def conversion(self, val):
        return val

    def json(self):
        return dict(
            index=self.index,
            id=self.id,
            display=self.display,
            type=self.type,      
            node=self.interface.name,
            value=self.current_value,
            change=self.change,
            data_rate=self.data_rate,
            decorator=self.decorator,
            cls=self.__class__.__name__
        )
