# -*- coding: utf-8 -*-
import serial
import gevent
import math
import io

class Event(object):

    def __init__(self, *args, **kwargs):
        gevent.spawn(self.run, *args, **kwargs)

    def run(self, *args, **kwargs): return

class SensorEvent(Event):
    def run(self, value):
        print "%s: %s" % (self.__class__.__name__, value)

class EventDispatcher(object):
    def __init__(self):
        self.handlers = []

    def __iadd__(self, handler):
        self.handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.handlers.remove(handler)
        return self

    def fire(self, *args, **keywargs):
        for handler in self.handlers:
            handler(*args, **keywargs)

class Sensor(EventDispatcher):
    name = ""
    change = 5
    value = 0

    def __init__(self, name, events=None, change=5):
        super(Sensor, self).__init__()
        self.name = name
        self.change = change
        self.handlers = events if events else []

    def do_conversion(self, value):
        self.value = self.conversion(value)
        return self.value

    def conversion(self, value):
        return value

class Arduino(object):
    running = True
    past_values = []

    def __init__(self, sensors, port=['/dev/ttyS0', '/dev/tty.usbmodemfa131'], baud=9600):
        self.port = port        
        self.baud = baud
        self.port_try = 0 
        self.try_serial()       
        self.running = True
        self.sensors = dict()
        self.sensor_ids = []
        for sensor in sensors:
            self.sensor_ids.append(sensor.name)
            self.sensors[sensor.name] = sensor
        self.past_values = [0 for i in xrange(100)]
        gevent.spawn(self.run)

    def try_serial(self):
        try:
            self.serial = serial.Serial(self.port[self.port_try], self.baud, timeout=1)
        except Exception as e:
            print e
            self.port_try+=1
            if self.port_try < len(self.port):
                self.try_serial()
            else:
                raise e

    def run(self):
        buffer = ''
        buffering = False
        while(self.running):
            try:
                ch = self.serial.read(size=1)
                if ch == "@" and not buffering: buffering = True
                if buffering and not ch == "!": buffer+=ch
                if ch == "!" and buffering:
                    buffering = False
                    buffer = buffer.lstrip("@")
                    buffer = buffer.rstrip("\r\n")
                    lines = buffer.split('\r\n')
                    print lines
                    buffer = ""
                    for data in lines:
                        sensor, value = data.split(",")
                        sensor = int(sensor)
                        value = float(value)
                        diff = math.fabs(self.past_values[sensor]-value)                        
                        d = self.sensors[self.sensor_ids[sensor]]
                        if diff > d.change or self.past_values[sensor] == 0:
                            #print "Diff: %s" % diff
                            self.past_values[sensor] = value
                            val = d.do_conversion(value)
                            d.fire(value=val)
            except Exception as e:                
                buffer = ""
                print e
            gevent.sleep(0)

    def digital(self, pin, val):
        st = "%s,%s\r" % (pin, val)
        return self.serial.write(st)


class ECEvent(SensorEvent): pass
class TDSEvent(SensorEvent): pass
class SalinityEvent(SensorEvent): pass
class DOEvent(SensorEvent): pass
class ORPEvent(SensorEvent): pass
class TempEvent(SensorEvent):
    def run(self, value):
        print "%s: %s˚C" % (self.__class__.__name__, value)

class HumidityEvent(SensorEvent):
    def run(self, value):
        print "%s: %s%%" % (self.__class__.__name__, value)

class WaterTempEvent(SensorEvent): pass
class PHEvent(SensorEvent): pass
class WaterLevelEvent(SensorEvent): pass

class Temperature(Sensor):
    voltage = 5.0
    def conversion(self, value):
        Tf = float(value)*5.0
        Tf = Tf/10
        Tc = float(Tf)-32
        diff = 5.0/9
        Tc = Tc*diff
        return Tc

class Humidity(Sensor):
    voltage = 5.0
    celcius = 25.0

    def conversion(self, value):
        volt = value/1023 * self.voltage
        rh = 161.0*volt/self.voltage-25.8
        true = rh/(1.0546-.0026*self.celcius)
        return true

        

ard = Arduino(sensors=[
    Sensor('PH', [PHEvent], change=25), 
    Sensor('EC', [ECEvent], change=25), 
    Sensor('TDS',[TDSEvent], change=20),
    Sensor('Salinity',[SalinityEvent]), 
    Sensor('DO Percentage',[DOEvent]), 
    Sensor('DO',[DOEvent]), 
    Sensor('ORP',[ORPEvent]), 
    Temperature('Temperature',[TempEvent], change=2),
    Humidity('Humidity',[HumidityEvent]),
    Temperature('Water Temperature',[WaterTempEvent]), 
    Sensor('Water Level',[WaterLevelEvent]),
])

class OtherWaterLevelEvent(WaterLevelEvent):pass

ard.sensors['Water Level']+=OtherWaterLevelEvent


while True:
    ard.digital(13,1)
    gevent.sleep(1)
    ard.digital(13,0)
    gevent.sleep(1)
