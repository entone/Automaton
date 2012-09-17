import settings

class Output(object):
    index = ""
    display = ""
    type = ""
    interface=None
    current_state = False

    def __init__(self, index, display, type, interface):
        self.logger = settings.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.index = index
        self.display = display
        self.type = type
        self.interface = interface

    def set_state(self, state):
        self.logger.debug("Setting Output: %s to: %s" % (self.json(), state))
        try:
            self.interface.interface_kit.setOutputState(self.index, state)
            self.current_state = state
        except Exception as e:
            self.logger.warning("No interface kit connected. Test Node?")
        return

    def get_state(self):
        return self.interface.interface_kit.getOutputState(self.index)

    def json(self):
        return dict(
            index=self.index,
            display=self.display,
            type=self.type,
            state=self.current_state,
            node=self.interface.name,
        )