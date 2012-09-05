from node import Node
from node.sensor.temperature import Temperature
from node.sensor.humidity import Humidity
from node.sensor.ph import PH
from node.output import Output

class Aquaponics(Node):

    def __init__(self, *args, **kwargs):
        temp = Temperature(0, 'Temperature', 'temp', self, change=2)
        humidity = Humidity(1, 'Humidity', 'humidity', self, change=10)
        ph = PH(2, 'PH', 'ph', self, change=20)
        self.sensors = [temp, humidity, ph,]

        plant_light = Output(0, 'Plant Light', 'plant_light', self)
        self.outputs = [plant_light,]

        super(Aquaponics, self).__init__(*args, **kwargs)
        
            