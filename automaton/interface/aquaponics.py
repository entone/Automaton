#!/usr/bin/env python

#Basic imports
from ctypes import *
import sys
import random
import logging
from util.publisher import Publisher 
#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, OutputChangeEventArgs, SensorChangeEventArgs
from Phidgets.Devices.InterfaceKit import InterfaceKit
import gevent
import json

#Create an interfacekit object

class Aquaponics(Publisher):
    CURRENT_CELCIUS = 30
    interface_kit = None
    NODE = 'lettuce'

    def __init__(self, *args, **kwargs):        
        self.sensors = dict(
            Temperature=dict(
                input=0,
                conversion=self.temperature_conversion,
                change=2,
                type='temp',
            ),
            Humidity=dict(
                input=1,
                conversion=self.humidity_conversion,
                change=10,
                type='humidity',
            ),
            PH=dict(
                input=2,
                conversion=self.ph_conversion,
                change=20, 
                type='ph'
            ),
        )
        try:
            self.interface_kit = InterfaceKit()
            print "starting: %s" % self.interface_kit
            super(Aquaponics, self).__init__(*args, **kwargs)
        except RuntimeError as e:
            print("Runtime Exception: %s" % e.details)
            print("Exiting....")

    def ph_conversion(self, value):
        #print "ORIG Value: %s" % value
        val = float(value)/200
        val = 2.5-val
        temp = .257179+(.000941468*float(self.CURRENT_CELCIUS))
        return 7-(val/temp)

    def humidity_conversion(self, value):
        #print "Orig Value: %s" % value
        val = ((.0004*float(self.CURRENT_CELCIUS)+.149)*float(value))-(.0617*float(self.CURRENT_CELCIUS)+ 24.436)
        return val
        value = float(value)/1000
        return value*100

    def temperature_conversion(self, value):
        base = float(5000)/1000
        Tf = float(value)*base
        Tf = Tf/10
        print "Farenheit: %s" % Tf
        Tc = float(Tf)-32
        diff = float(5)/9
        Tc = Tc*diff
        self.CURRENT_CELCIUS = Tc
        return Tc

    def get_sensor(self, index):
        for name, sens in self.sensors.iteritems():
            if index == sens.get('input'):
                return (name, sens)

        return False

    def get_values(self, obj):
        res = {}
        for name, sensor in self.sensors.iteritems():
            val = sensor.get('conversion')(self.interface_kit.getSensorValue(sensor.get('input')))
            res[sensor.get('type')] = dict(value=val, node=self.NODE)

        return res

    #Information Display Function
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
        try:
            name, sensor = self.get_sensor(e.index)
        except: return
        val = sensor['conversion'](e.value) if sensor else 0
        source = e.device
        ob = dict(node=self.NODE, type=sensor.get('type'), value=val)
        self.publish(ob)
        print("%s Sensor: %s" % (name, val))

    def interfaceKitOutputChanged(self, e):
        source = e.device
        print("InterfaceKit %i: Output %i: %s" % (source.getSerialNum(), e.index, e.state))

    def run(self):
        print "RUN!"
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
                try:
                    name, sensor = self.get_sensor(i)
                except: continue
                print "Setting Up: %s" % name
                self.interface_kit.setSensorChangeTrigger(i, sensor.get("change"))
                self.interface_kit.setDataRate(i, 4)
            except PhidgetException as e:
                print("Phidget Exception %i: %s" % (e.code, e.details))
            