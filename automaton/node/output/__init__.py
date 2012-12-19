import settings
import util

class MockEvent(object):
    def __init__(self, index, state):
        self.index = index
        self.state = state

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
        self.interface = interface

    def set_state(self, state):
        self.logger.debug("Setting Output: %s to: %s" % (self.json(), state))
        try:
            self.interface.interface_kit.setOutputState(self.index, state)
            self.current_state = state
        except Exception as e:
            self.interface.interfaceKitOutputChanged(MockEvent(self.index, state))
            self.logger.warning("Mock Event")
        return

    def get_state(self):
        return self.interface.interface_kit.getOutputState(self.index)

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