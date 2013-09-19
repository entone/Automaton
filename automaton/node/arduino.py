# -*- coding: utf-8 -*-
import serial
import gevent
import math
import random
import io
import util

class Arduino(object):
    running = True
    past_values = []
    outputs = []

    def __init__(self, sensors, port=['/dev/ttyS0', '/dev/tty.usbmodemfa131'], baud=9600):
        self.port = port        
        self.baud = baud
        self.port_try = 0        

        self.running = True
        self.sensors = dict()
        self.sensor_ids = []
        for sensor in sensors:
            self.sensor_ids.append(sensor.display)
            self.sensors[sensor.display] = sensor
        self.past_values = [0 for i in xrange(100)]
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        try:
            self.try_serial()       
            gevent.spawn(self.run)
        except serial.serialutil.SerialException as e:
            gevent.spawn(self.run_test)
        

    def try_serial(self):
        try:
            self.serial_conn = serial.Serial(self.port[self.port_try], self.baud, timeout=1)
            self.sio = io.TextIOWrapper(io.BufferedRWPair(self.serial_conn, self.serial_conn, 1))
        except Exception as e:
            self.port_try+=1
            if self.port_try < len(self.port):
                self.try_serial()
            else:
                raise e

    def run(self):
        buffering = False
        while(self.running):
            try:
                data = self.sio.readline().rstrip()
                sensor, value = data.split(",")
                sensor = int(sensor)
                value = float(value)
                diff = math.fabs(self.past_values[sensor]-value)
                d = self.sensors[self.sensor_ids[sensor]]                
                if diff > d.change or (self.past_values[sensor] == 0 and diff > 0):
                    self.past_values[sensor] = value
                    val = d.do_conversion(value)
                    d.fire(message=d.json())
            except Exception as e:
                self.logger.warning("Bad Data: %s" % data)
                self.logger.warning(e)
            gevent.sleep(0)

    def run_test(self):
        while(self.running):
            for key, sensor in self.sensors.iteritems():
                sensor.do_conversion(random.randint(0, 100))
                sensor.fire(message=sensor.json())
                gevent.sleep(5)

    def digital(self, pin, val):
        val = 0 if val == False else 1
        st = "D|%s|%s\r" % (pin, val)
        try:
            self.logger.info("Setting: %s" % st)
            return self.serial_conn.write(st)
        except Exception as e:
            self.logger.warning(e)
        return

    def serial(self, pin, val):
        st = "S|%s|%s\r" % (pin, val)
        try:
            return self.serial_conn.write(st)
        except Exception as e:
            self.logger.warning(e)

    def pause(self):
        try:
            return self.serial_conn.write("P\r")
        except Exception as e:
            self.logger.warning(e)
        

    def resume(self):
        try:
            return self.serial_conn.write("R\r")
        except Exception as e:
            self.logger.warning(e)


