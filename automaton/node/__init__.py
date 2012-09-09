from ctypes import *
import sys
import random
import logging
from util.publisher import Publisher
from util.jsontools import ComplexEncoder
from loggers import Logger
#Phidget specific imports
LIVE = True
try:
    from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
    from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, OutputChangeEventArgs, SensorChangeEventArgs
    from Phidgets.Devices.InterfaceKit import InterfaceKit
except:
    LIVE = False

import gevent
import simplejson as json

class Node(Publisher):

    name = None
    sensors = []
    outputs = []
    inputs = []
    triggers = []
    clocks = []
    interface_kit = None

    def __init__(self, name, *args, **kwargs):
        self.name = name
        if LIVE: self.interface_kit = InterfaceKit()
        super(Node, self).__init__(*args, **kwargs)

    def get_sensor(self, index):
        for sensor in self.sensors:
            if sensor.index == index: return sensor

        return False

    def get_output(self, index):
        for output in self.outputs:
            if output.index == index: return output

        return False

    def get_sensor_values(self, ob):
        res = {}
        for sensor in self.sensors:
            res[sensor.type] = sensor.json()

        return res

    def get_output_values(self):
        res = {}
        for output in self.outputs:
            res[ouput.type] = output.json()

        return res    

    def set_output_state(self, ob):
        output = self.get_output(ob.get('index'))
        if output:
            print "%s: turning %s to %s index: %s" % (self.name, ob.get('type'), ob.get('state'), output.index)
            output.set_state(ob.get('state'))
            return dict(state=output.current_state)

    def json(self):
        return dict(
            name=self.name,
            sensors=[s.json() for s in self.sensors],
            outputs=[o.json() for o in self.outputs],
            inputs=[i.json() for i in self.inputs],
            triggers=[t.json() for t in self.triggers],
        )

    def __conform__(self, protocol):
        return json.dumps(self.json(), cls=ComplexEncoder)

    def displayDeviceInfo(self):
        print("|------------|----------------------------------|--------------|------------|")
        print("|- Attached -|-              Type              -|- Serial No. -|-  Version -|")
        print("|------------|----------------------------------|--------------|------------|")
        print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (self.interface_kit.isAttached(), self.interface_kit.getDeviceName(), self.interface_kit.getSerialNum(), self.interface_kit.getDeviceVersion()))
        print("|------------|----------------------------------|--------------|------------|")
        print("Number of Digital Inputs: %i" % (self.interface_kit.getInputCount()))
        print("Number of Digital Outputs: %i" % (self.interface_kit.getOutputCount()))
        print("Number of Sensor Inputs: %i" % (self.interface_kit.getSensorCount()))

    #Event Handler Callback Functions
    def inferfaceKitAttached(self, e):
        attached = e.device
        print("InterfaceKit %i Attached!" % (attached.getSerialNum()))

    def interfaceKitDetached(self, e):
        detached = e.device
        print("InterfaceKit %i Detached!" % (detached.getSerialNum()))

    def interfaceKitError(self, e):
        try:
            source = e.device
            print("InterfaceKit %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))

    def interfaceKitInputChanged(self, e):
        source = e.device
        print("InterfaceKit %i: Input %i: %s" % (source.getSerialNum(), e.index, e.state))

    def interfaceKitSensorChanged(self, e):
        sensor = self.get_sensor(e.index)
        if not sensor: return
        val = sensor.do_conversion(float(e.value)) if sensor else 0
        source = e.device
        ob = sensor.json()
        self.publish(ob)
        print("%s Sensor: %s" % (sensor.display, val))

    def interfaceKitOutputChanged(self, e):
        output = self.get_output(e.index)
        if not output: return
        output.current_state = e.state
        self.publish(output.json())
        source = e.device
        print("%s Output: %s" % (output.display, output.current_state))


    def run(self):
        try:
            self.interface_kit.setOnAttachHandler(self.inferfaceKitAttached)
            self.interface_kit.setOnDetachHandler(self.interfaceKitDetached)
            self.interface_kit.setOnErrorhandler(self.interfaceKitError)
            self.interface_kit.setOnInputChangeHandler(self.interfaceKitInputChanged)
            self.interface_kit.setOnOutputChangeHandler(self.interfaceKitOutputChanged)
            self.interface_kit.setOnSensorChangeHandler(self.interfaceKitSensorChanged)
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Exiting....")

        print("Opening phidget object....")

        try:
            self.interface_kit.openPhidget()
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Exiting....")

        print("Waiting for attach....")

        try:
            self.interface_kit.waitForAttach(10000)
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            try:
                self.interface_kit.closePhidget()
            except PhidgetException as e:
                print("Phidget Exception %i: %s" % (e.code, e.details))
                print("Exiting....")
                exit(1)
            print("Exiting....")
        else:
            self.displayDeviceInfo()

        print("Setting the data rate for each sensor index to 10ms....")
        for i in range(self.interface_kit.getSensorCount()):
            try:
                sensor = self.get_sensor(i)
                if sensor:
                    print "Setting Up: %s" % sensor.display
                    print "Change: %s" % sensor.change
                    print "Data Rate: %s" % sensor.data_rate
                    self.interface_kit.setSensorChangeTrigger(i, sensor.change)
                    self.interface_kit.setDataRate(i, 4)
            except PhidgetException as e:
                print("Phidget Exception %i: %s" % (e.code, e.details))

        self.logger = Logger(node=self)