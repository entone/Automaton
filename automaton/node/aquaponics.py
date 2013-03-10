from node import Node
from node.sensor import Sensor
from node.sensor.temperature import Temperature
from node.sensor.humidity import Humidity
from node.sensor.ph import PH
from node.sensor.light import Light
from node.sensor.etape import ETape
from node.sensor.dissolved_oxygen import DissolvedOxygen

from node.output import Output
from node.trigger import Trigger
from node.trigger import Clock
from node.trigger import PID
from node.trigger import Repeater
import settings

class Aquaponics(Node):

    def __init__(self ,*args, **kwargs):
        ph = PH('PH', self, [self.publish], change=.1)
        ec = Sensor('EC', self, [self.publish], change=25, typ="ec")
        tds = Sensor('TDS', self, [self.publish], change=10, typ="tds")
        sal = Sensor('Salinity', self, [self.publish], change=1, typ="salinity")
        do_per = Sensor('DO Percentage', self, [self.publish], change=.1, typ="do_percentage")
        do = DissolvedOxygen('DO', self, [self.publish], change=.1, typ="do")
        orp = Sensor('ORP', self, [self.publish], typ="orp")
        humidity = Humidity('Humidity', self,[self.publish])
        temp = Temperature('Temperature', self, [self.publish], 
            updaters=[humidity.set_temp, ph.set_temp, do.set_temp], change=1
        )
        water_temp = Temperature('Water Temperature', self, [self.publish])
        level = ETape('Water Level', self, [self.publish], change=100)
                
        self.sensors = [ph, ec, tds, sal, do_per, do, orp, temp, humidity, water_temp, level]

        super(Aquaponics, self).__init__(*args, **kwargs)
        
            
