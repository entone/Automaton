import random
import gevent
import settings
from node import Node
from node.sensor.temperature import Temperature
from node.sensor.humidity import Humidity
from node.sensor.ph import PH
from node.output import Output
from node.input import Input
from node.trigger import Trigger
from node.trigger import Repeater
from node.trigger import Clock
from node.trigger import PID

class Test(Node):

    def __init__(self, name, *args, **kwargs):
        #Output
        self.plant_light = Output(0, 'Foilage', 'plant_light', self)
        self.fan = Output(1, 'Fan', 'fan', self)
        self.pump = Output(2, 'Pump', 'pump', self)
        self.subpump = Output(3, 'SubPump', 'subpump', self)
        self.laser = Output(4, 'Laser', 'laser', self)
        self.outputs = [self.plant_light, self.fan, self.pump, self.subpump, self.laser,]

        #Sensors
        self.temp = Temperature(0, 'Temperature', 'temp', self, change=2)
        self.humidity = Humidity(1, 'Humidity', 'humidity', self, change=10)
        self.ph = PH(2, 'PH', 'ph', self, change=20)
        self.sensors = [self.temp, self.humidity, self.ph,]
        #Inputs
        self.motion = Input(0, 'Motion Detector', 'motion_detector', self)
        self.inputs = [self.motion]
        #Repeaters
        pump_repeater = Repeater(self.pump, run_for=15, every=60, state=True)
        subpump_repeater = Repeater(self.subpump, run_for=15, every=60, state=True, padding=2)
        self.repeaters = [pump_repeater, subpump_repeater]
        #Clocks
        light_on = Clock(time=(12,0), output=self.plant_light, state=True)
        light_off = Clock(time=(0,0), output=self.plant_light, state=False)         
        pump2_on = Clock(time=(10,0), output=self.subpump, state=True) 
        pump2_off = Clock(time=(20,0), output=self.subpump, state=False) 
        self.clocks = [light_on, light_off, pump2_on, pump2_off]
        #Triggers
        trig = Trigger(input=self.temp, output=self.fan, min=30, max=float('inf'), state=True, current_state=False)
        motion = Trigger(input=self.motion, output=self.laser, min=True, max=None, state=True, current_state=False)
        pid = PID(input=self.temp, output=self.fan, state=True, set_point=27, P=3.0, I=0.4, D=1.2)

        self.triggers = [trig, motion]

        super(Test, self).__init__(name, *args, **kwargs)
        
    def run(self):
        while True:
            gevent.sleep(10)
            self.temp.current_value = random.randint(0, 50)
            self.publish(self.temp.json())
            
            self.humidity.current_value = random.randint(0, 100)
            self.publish(self.humidity.json())

            self.ph.current_value = random.randint(0, 14)
            self.publish(self.ph.json())

            self.motion.current_value = not self.motion.current_value
            self.publish(self.motion.json())            
        





