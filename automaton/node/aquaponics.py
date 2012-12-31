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

    def __init__(self ,*args, **kwargs):        
        water_temp = Temperature(0, 'Water Temperature', self, change=5)
        ph = PH(1, 'PH', self, change=20)        
        temp = Temperature(2, 'Temperature', self, change=5)
        humidity = Humidity(3, 'Humidity', self, change=5)
        level = ETape(7, 'Water Level', self, change=1)         
        
        
        self.sensors = [water_temp, ph, temp, humidity, level]

        plant_light = Output(0, 'Plant Light', self)
        aqua_light = Output(1, 'Aqua Light', self)
        self.outputs = [plant_light, aqua_light]

        light_on = Clock((12,00), plant_light, True)
        light_off = Clock((0, 1), plant_light, False)

        aqua_light_on = Clock((12,00), aqua_light, True)
        aqua_light_off = Clock((0, 1), aqua_light, False)

        self.clocks = [light_on, light_off, aqua_light_on, aqua_light_off]

        super(Aquaponics, self).__init__(*args, **kwargs)
        
            
