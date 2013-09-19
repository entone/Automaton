from automaton.node.sensor import Sensor

class Humidity(Sensor):
    voltage = 5.0
    celcius = 25.0
    type="humidity"
    decorator="%"

    def conversion(self, value):
        volt = value/1023 * self.voltage
        rh = 161.0*volt/self.voltage-25.8
        true = rh/(1.0546-.0026*self.celcius)
        return true

    def set_temp(self, value):
    	self.celcius = value


