from node.sensor import Sensor

class DissolvedOxygen(Sensor):
    type="do"
    decorator="ppm"

    def conversion(self, value):
        return float(value)

    def set_temp(self, val):
        return self.interface.interface_kit.serial(2, "%s,0"%val)


