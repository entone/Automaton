from node.sensor import Sensor

class Temperature(Sensor):
    decorator = "&deg;C"
    type="temperature"

    def conversion(self, value):
        base = float(5000)/1000
        Tf = float(value)*base
        Tf = Tf/10
        Tc = float(Tf)-32
        diff = float(5)/9
        Tc = Tc*diff
        self.set_temp(Tc)
        return Tc

    def set_temp(self, val):
    	for sensor in self.interface.sensors:
    		try:
    			sensor.set_temp(val)
    		except: pass