import settings
import util

class Output(object):
    index = ""
    display = ""
    type = ""
    id = ""
    interface=None
    current_state = False

    def __init__(self, index, display, interface):
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.index = index
        self.display = display
        self.id = util.slugify(self.display)
        self.type = util.slugify(display)
        self.logger.info(self.type)
        self.interface = interface

    def set_state(self, state):
        self.logger.info("Setting Output: %s to: %s" % (self.json(), state))
        self.interface.digital(self.index, state)
        self.current_state = state
        self.interface.publish(message=self.json())
        return

    def get_state(self):
        return self.current_state

    def json(self):
        return dict(
            id=self.id,
            index=self.index,
            display=self.display,
            type=self.type,
            state=self.current_state,
            value=self.current_state,
            node=self.interface.name,
            cls=self.__class__.__name__
        )