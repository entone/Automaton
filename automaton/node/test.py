import random
import gevent
from node import Node
from node.sensor.temperature import Temperature
from node.sensor.humidity import Humidity
from node.sensor.ph import PH
from node.output import Output
from node.trigger import Trigger

class Test(Node):

    def __init__(self, *args, **kwargs):
        self.plant_light = Output(0, 'Foilage', 'plant_light', self)
        self.fan = Output(1, 'Fan', 'fan', self)
        self.pump = Output(2, 'Pump', 'pump', self)
        self.pump1 = Output(2, 'Pump1', 'pump1', self)
        self.pump2 = Output(2, 'Pump2', 'pump2', self)
        self.outputs = [self.plant_light, self.fan, self.pump,self.pump1,self.pump2,]

        self.temp = Temperature(0, 'Temperature', 'temp', self, change=2)
        self.humidity = Humidity(1, 'Humidity', 'humidity', self, change=10)
        self.ph = PH(2, 'PH', 'ph', self, change=20)
        self.sensors = [self.temp, self.humidity, self.ph,]

        trig = Trigger(input=self.temp, output=self.fan, min=30, max=float('inf'), state=True, current_state=False, port=kwargs.get("publisher"))
        self.triggers = [trig]

        super(Test, self).__init__(*args, **kwargs)
        
    def run(self):
        gevent.spawn(self.fake_numbers)

    def fake_numbers(self):
        while True:
            self.temp.current_value = random.randint(0, 50)
            self.publish(self.temp.json())
            
            self.humidity.current_value = random.randint(0, 100)
            self.publish(self.humidity.json())

            self.ph.current_value = random.randint(0, 14)
            self.publish(self.ph.json())

            gevent.sleep(20)





