from node.sensor import Sensor

class PH(Sensor):   
    type="ph"
    decorator=""

    def conversion(self, value):
        return value

    def set_temp(self, val):
        return self.interface.interface_kit.serial(0, val)


