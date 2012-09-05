from node.sensor import Sensor

class Humidity(Sensor):
    celcius = 30
    decorator = "%"

    def conversion(self, value):
        val = ((.0004*float(self.celcius)+.149)*float(value))-(.0617*float(self.celcius)+ 24.436)
        return val

    def set_temp(self, val):
        self.celcius = val


