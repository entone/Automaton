from node import Node
from node.sensor.temperature import Temperature
from node.sensor.humidity import Humidity
from node.sensor.ph import PH
from node.sensor.light import Light

from node.output import Output
from node.trigger import Trigger
from node.trigger import Clock
from node.trigger import PID
import settings

class Aquaponics(Node):

    def __init__(self, name, *args, **kwargs):
        temp = Temperature(0, 'Temperature', 'temp', self, change=10)
        water_temp = Temperature(1, 'Water Temperature', 'water_temp', self, change=5)
        humidity = Humidity(2, 'Humidity', 'humidity', self, change=5)
        ph = PH(3, 'PH', 'ph', self, change=20)
        light = Light(4, 'Light', 'light', self, change=20)

        self.sensors = [temp, water_temp, humidity, ph, light,]

        plant_light = Output(0, 'Plant Light', 'plant_light', self)
        heater = Output(1, 'Heater', 'heater', self)
        pump = Output(2, 'Fish Pump', 'fish_pump', self)
        fan = Output(3, 'Fan', 'fan', self)
        self.outputs = [plant_light,heater,pump, fan]

        trig = Trigger(input=temp, output=fan, min=30, max=float('inf'), state=True, current_state=False)
        pid = PID(input=water_temp, output=heater, state=True, set_point=27, P=3.0, I=0.4, D=1.2)
        self.triggers = [trig,]

        light_on = Clock((12,00), plant_light, True)
        light_off = Clock((0, 1), plant_light, False)

        self.clocks = [light_on, light_off]

        super(Aquaponics, self).__init__(name, *args, **kwargs)
        
            
