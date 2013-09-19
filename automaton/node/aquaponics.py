from automaton.node import Node
from automaton.node.sensor import Sensor
from automaton.node.sensor.temperature import Temperature
from automaton.node.sensor.humidity import Humidity
from automaton.node.sensor.ph import PH
from automaton.node.sensor.light import Light
from automaton.node.sensor.etape import ETape
from automaton.node.sensor.dissolved_oxygen import DissolvedOxygen

from automaton.node.output import Output
from automaton.node.trigger import Trigger
from automaton.node.trigger import Clock
from automaton.node.trigger import PID
from automaton.node.trigger import Repeater
from automaton import settings

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

        lights = Output(0, "Lights", self)
        test = Output(13, "Debug", self)

        self.outputs = [lights, test]

        self.clocks = [Clock([13,0], lights, True), Clock([1,0], lights, False)]
        self.sensors = [ph, ec, tds, sal, do_per, do, orp, temp, humidity, water_temp, level]

        super(Aquaponics, self).__init__(*args, **kwargs)
        
            
