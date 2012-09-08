from node.sensor import Sensor

class PH(Sensor):   
    celcius = 30
    ph="ph"

    def conversion(self, value):
        val = float(value)/200
        val = 2.5-val
        temp = .257179+(.000941468*float(self.celcius))
        return 7-(val/temp)

    def set_temp(self, val):
        self.celcius = val


