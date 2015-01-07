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
from node.input import Input
import settings
import gevent
import random

class Test(Node):

    def __init__(self ,*args, **kwargs):
        self.ph = PH('PH', self, [self.publish], change=.1)
        self.tds = Sensor('TDS', self, [self.publish], change=10, typ="tds")
        self.do = DissolvedOxygen('DO', self, [self.publish], change=.1, typ="do")
        self.humidity = Humidity('Humidity', self,[self.publish])
        self.temp = Temperature('Temperature', self, [self.publish],
            updaters=[self.humidity.set_temp, self.ph.set_temp, self.do.set_temp], change=1
        )
        self.water_temp = Temperature('Water Temperature', self, [self.publish])
        self.level = ETape('Water Level', self, [self.publish], change=100)

        self.lights = Output(None, "Lights", self)
        self.test = Output(None, "Debug", self)

        self.lights_detected = Input(None, "Light Detected", self)

        self.outputs = [self.lights, self.test]
        self.inputs = [self.lights_detected,]

        self.clocks = [Clock([13,0], self.lights, True), Clock([1,0], self.lights, False)]
        self.sensors = [self.ph, self.tds, self.do, self.temp, self.humidity, self.water_temp, self.level]

        super(Test, self).__init__(*args, **kwargs)


    def run(self):
        while True:
            gevent.sleep(2)
            self.ph.do_conversion(random.randint(3, 14))
            self.publish(self.ph.json())

            self.tds.do_conversion(random.randint(0, 50))
            self.publish(self.tds.json())

            self.humidity.do_conversion(random.randint(1000, 1023))
            self.publish(self.humidity.json())

            self.temp.do_conversion(random.randint(100, 160))
            self.publish(self.temp.json())

            self.water_temp.do_conversion(random.randint(100, 160))
            self.publish(self.water_temp.json())

            self.level.do_conversion(random.randint(5,35))
            self.publish(self.level.json())

            val = random.randint(0,1)
            self.lights_detected.do_conversion(val)
            self.publish(self.lights_detected.json())
