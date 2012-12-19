import settings
import util

class Input(object):
    index = ""
    display = ""
    id = ""
    current_value = False
    interface = None
    decorator = ""
    type = ""

    def __init__(self, index, display, type, interface):
        self.index = index
        self.display = display
        self.type = type
        self.interface = interface
        self.id = util.slugify(self.display)
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))

    def do_conversion(self, val): 
        self.current_value = val
        return self.current_value

    def get_value():
        return self.current_value

    def json(self):
        return dict(
            id=self.id,
            index=self.index,
            display=self.display,
            type=self.type,      
            node=self.interface.name,
            value=self.current_value,
            decorator=self.decorator,
            cls=self.__class__.__name__
        )