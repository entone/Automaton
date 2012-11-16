from node.sensor import Sensor

class ETape(Sensor):
    decorator = 'cm'
    type="temp"
    RESISTOR = 550
    MIN = 208.0
    MAX = 1457.0
    HEIGHT = 21

    def conversion(self, value):
        self.logger.info("RAW: %s" % value)
        value = (1000/value) - 1
        value = self.RESISTOR/value
        val = int(value)
        self.logger.info("Resistance: %s" % val)
        val = (self.MAX-val)/(self.MAX-self.MIN)
        self.logger.info(val)
        return val*self.HEIGHT

