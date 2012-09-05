from interface import Interface
import interface.sensor as sensor
import interface.output as output

class Aquaponics(Interface):

    def __init__(self, *args, **kwargs):
        temp = sensor.Temperature(0, 'Temperature', 'temp', self, change=2)
        humidity = sensor.Humidity(1, 'Humidity', 'humidity', self, change=10)
        ph = sensor.PH(2, 'PH', 'ph', self, change=20)
        self.sensors = [temp, humidity, ph,]

        plant_light = output.Output(0, 'Plant Light', 'plant_light', self)
        self.outputs = [plant_light,]

        super(Aquaponics, self).__init__(*args, **kwargs)
        
            