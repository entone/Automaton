from node import Node
from node.sensor.temperature import Temperature
from node.sensor.humidity import Humidity
from node.sensor.ph import PH
from node.sensor.light import Light

from node.output import Output
from node.trigger import Trigger
from node.trigger import Clock

class Aquaponics(Node):

    def __init__(self, *args, **kwargs):
        temp = Temperature(0, 'Temperature', 'temp', self, change=10)
        humidity = Humidity(1, 'Humidity', 'humidity', self, change=10)
        ph = PH(2, 'PH', 'ph', self, change=20)
        light = Light(3, 'Light', 'light', self, change=20)

        self.sensors = [temp, humidity, ph, light,]

        plant_light = Output(0, 'Plant Light', 'plant_light', self)
        fan = Output(1, 'Cooling Fan', 'cooling_fan', self)
        self.outputs = [plant_light,fan]

        trig = Trigger(input=temp, output=fan, min=30, max=float('inf'), state=True, current_state=False, port=kwargs.get("publisher"))
        trig2 = Trigger(input=light, output=plant_light, min=0, max=60, state=True, current_state=False, port=kwargs.get("publisher"))
        self.triggers = [trig, trig2]

        light_on = Clock((12,00), plant_light, True)
        light_off = Clock((0, 1), plant_light, False)

        self.clocks = [light_on, light_off]

        super(Aquaponics, self).__init__(*args, **kwargs)
        
            