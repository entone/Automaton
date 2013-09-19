from automaton.node.sensor import Sensor

class Light(Sensor):
    type="light"
    decorator = "%"

    def conversion(self, value):
        return float(value)/10