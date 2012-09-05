class Sensor(object):
    index = ""
    display = ""
    type = ""
    change = 2
    data_rate = 10
    current_value = 0
    interface = None

    def __init__(self, index, display, type, interface, change=2, data_rate=10):
        self.index = index
        self.display = display
        self.type = type
        self.change = change
        self.data_rate = data_rate
        self.interface = interface

    def do_conversion(self, val): 
        self.current_value = self.conversion(float(val))
        return self.current_value

    def get_value():
        return self.do_conversion(self.interface.interface_kit.getSensorValue(self.index))

    def json(self):
        return dict(
            index=self.index,
            display=self.display,
            type=self.type,      
            node=self.interface.node,
            value=self.current_value
        )