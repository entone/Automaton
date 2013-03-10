from node.sensor import Sensor

class ETape(Sensor):
    decorator = 'cm'
    type="etape"
    RESISTOR = 550
    MIN = 208.0
    MAX = 1457.0
    HEIGHT = 21

    def conversion(self, value):
        value = (1000/value) - 1
        value = self.RESISTOR/value
        val = int(value)
        val = (self.MAX-val)/(self.MAX-self.MIN)
        return val*self.HEIGHT

