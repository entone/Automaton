from node import Node
from node.sensor.temperature import Temperature
from node.sensor.humidity import Humidity
from node.sensor.ph import PH
from node.sensor.light import Light
from node.sensor.etape import ETape

from node.output import Output
from node.trigger import Trigger
from node.trigger import Clock
from node.trigger import PID
from node.trigger import Repeater
import settings

class Aquaponics(Node):

    def __init__(self, name, *args, **kwargs):
        #level = ETape(0, 'E-Tape', 'etape', self, change=1)
        temp = Temperature(0, 'Temperature', self, change=5)
        water_temp = Temperature(1, 'Water Temperature', self, change=5)
        humidity = Humidity(2, 'Humidity', self, change=5)
        #ph = PH(3, 'PH', 'ph', self, change=20)
        #light = Light(4, 'Light', 'light', self, change=20)
        self.sensors = [temp, water_temp, humidity,]

        plant_light = Output(0, 'Plant Light', self)
        heater = Output(1, 'Heater', self)
        pump = Output(2, 'Fish Pump', self)
        fan = Output(3, 'Fan', self)
        self.outputs = [plant_light,heater,pump, fan]

        trig = Trigger(input=temp, output=fan, min=30, max=float('inf'), state=True, current_state=False)
        pid = PID(input=water_temp, output=heater, state=True, set_point=27, P=3.0, I=0.4, D=1.2)
        
        self.triggers = [trig,]

        light_on = Clock((12,00), plant_light, True)
        light_off = Clock((0, 1), plant_light, False)

        self.clocks = [light_on, light_off]

        pump_timing = Repeater(output=pump, run_for=15, every=30)
        self.repeaters = [pump_timing,]

        super(Aquaponics, self).__init__(name, *args, **kwargs)
        
            
