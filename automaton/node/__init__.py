from ctypes import *
import sys
import random
import logging
import base64
import zmq.green as zmq
from util.pubsub import PubSub
from util.jsontools import ComplexEncoder
from util import aes
from loggers import Logger
import settings
import gevent
import simplejson as json
import util
#Phidget specific imports
LIVE = True
try:
    from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
    from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, OutputChangeEventArgs, SensorChangeEventArgs
    from Phidgets.Devices.InterfaceKit import InterfaceKit
except:
    LIVE = False

class Node(object):

    name = None
    sensors = []
    outputs = []
    inputs = []
    triggers = []
    clocks = []
    repeaters = []
    interface_kit = None
    webcam=None

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name', 'Node')
        self.webcam = kwargs.get('webcam', '')
        self.initializing = True
        if LIVE: self.interface_kit = InterfaceKit()
        self.manager = PubSub(self, pub_port=settings.NODE_PUB, sub_port=settings.NODE_SUB, sub_filter=self.name)
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.initialize()    
        self.run()

    def initialize(self):
        while self.initializing:            
            self.logger.info("Waiting for manager")
            json = dict(name=self.name, method='add_node')
            self.publish(json)
            gevent.sleep(1)
        return

    def publish(self, message):
        message['name'] = self.name
        message['method'] = message.get('method', 'node_change')
        self.manager.publish(aes.encrypt(json.dumps(message, cls=ComplexEncoder), settings.KEY))
        self.test_triggers(message)

    def test_triggers(self, message):
        for t in self.triggers:
            t.handle_event(message)

    def initialize_rpc(self, obj, **kwargs):
        rpc = zmq.Context()
        rpc_socket = rpc.socket(zmq.REP)
        rpc_socket.bind("tcp://*:%s" % obj.get('port'))
        self.logger.info("RPC listening on: %s" % obj.get('port'))
        settings.KEY = base64.urlsafe_b64decode(str(obj.get('key')))
        self.logger.info("%s Initialized" % self.name)        
        while True:                    
            if self.initializing:
                self.initializing = False
                self.publish(dict(method='initialized'))

            message = aes.decrypt(rpc_socket.recv(), settings.KEY)
            ob = json.loads(message)
            try:
                res = getattr(self, ob.get("method"))(ob)
                st = json.dumps(res, cls=ComplexEncoder)
                rpc_socket.send(aes.encrypt(st, settings.KEY))
            except Exception as e:
                self.logger.exception(e)
            gevent.sleep(.1)

    def hello(self, obj):
        o = self.json()
        self.logger.info(o)
        return o

    def get_sensor(self, index):
        for sensor in self.sensors:
            if sensor.index == index: return sensor

        return False

    def get_output(self, index):
        for output in self.outputs:
            if output.index == index: return output

        return False

    def get_input(self, index):
        for input in self.inputs:
            if input.index == index: return input

        return False

    def get_sensor_values(self, ob):
        res = {}
        for sensor in self.sensors:
            res[sensor.id] = sensor.json()

        return res

    def get_output_values(self):
        res = {}
        for output in self.outputs:
            res[ouput.id] = output.json()

        return res    

    def set_output_state(self, ob):
        output = self.get_output(ob.get('index'))
        if output:
            self.logger.info("%s: turning %s to %s index: %s" % (self.name, ob.get('type'), ob.get('state'), output.index))
            output.set_state(ob.get('state'))
            return dict(state=output.current_state)

    def json(self, ob=None):
        return dict(
            name=self.name,
            webcam=self.webcam,
            sensors=[s.json() for s in self.sensors],
            outputs=[o.json() for o in self.outputs],
            inputs=[i.json() for i in self.inputs],
            triggers=[t.json() for t in self.triggers],
            repeaters=[r.json() for r in self.repeaters],
            clocks=[c.json() for c in self.clocks],            
            cls=self.__class__.__name__
        )

    def __conform__(self, protocol):
        return json.dumps(self.json(), cls=ComplexEncoder)

    def displayDeviceInfo(self):pass
        
    #Event Handler Callback Functions
    def inferfaceKitAttached(self, e):
        attached = e.device
        self.logger.info("InterfaceKit %i Attached!" % (attached.getSerialNum()))

    def interfaceKitDetached(self, e):
        detached = e.device
        self.logger.info("InterfaceKit %i Detached!" % (detached.getSerialNum()))

    def interfaceKitError(self, e):
        try:
            if e.eCode not in (36866,):
                source = e.device
                self.logger.info("InterfaceKit %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
        except PhidgetException as e:
            self.logger.exception(e)

    def interfaceKitInputChanged(self, e):
        input = self.get_input(e.index)
        if not input: return
        val = input.do_conversion(e.value)
        ob = input.json()
        self.publish(ob)
        self.logger.info("%s Input: %s" % (input.display, val))

    def interfaceKitSensorChanged(self, e):
        sensor = self.get_sensor(e.index)
        if not sensor: return
        val = sensor.do_conversion(float(e.value)) if sensor else 0
        ob = sensor.json()
        self.publish(ob)
        self.logger.info("%s Sensor: %s" % (sensor.display, val))

    def interfaceKitOutputChanged(self, e):
        output = self.get_output(e.index)
        if not output: return
        output.current_state = e.state
        ob = output.json()
        self.publish(ob)
        self.logger.info("%s Output: %s" % (output.display, output.current_state))


    def run(self):
        if LIVE: self.init_kit()
        while True: gevent.sleep(.1)

    def init_kit(self):
        try:
            self.interface_kit.setOnAttachHandler(self.inferfaceKitAttached)
            self.interface_kit.setOnDetachHandler(self.interfaceKitDetached)
            self.interface_kit.setOnErrorhandler(self.interfaceKitError)
            self.interface_kit.setOnInputChangeHandler(self.interfaceKitInputChanged)
            self.interface_kit.setOnOutputChangeHandler(self.interfaceKitOutputChanged)
            self.interface_kit.setOnSensorChangeHandler(self.interfaceKitSensorChanged)
        except PhidgetException as e:
            self.logger.exception(e)
            
        self.logger.info("Opening phidget object....")

        try:
            self.interface_kit.openPhidget()
        except PhidgetException as e:
            self.logger.exception(e)
            
        self.logger.info("Waiting for attach....")

        try:
            self.interface_kit.waitForAttach(10000)
        except PhidgetException as e:
            self.logger.exception(e)
            try:
                self.interface_kit.closePhidget()
            except PhidgetException as e:
                self.logger.exception(e)
                self.logger.info("Exiting....")
                exit(1)
            self.logger.info("Exiting....")
        else:
            self.displayDeviceInfo()

        self.logger.info("Initializing Sensors")
        for i in range(self.interface_kit.getSensorCount()):
            try:
                sensor = self.get_sensor(i)
                if sensor:
                    self.logger.info("Setting Up: %s" % sensor.display)
                    self.logger.info("Change: %s" % sensor.change)
                    self.logger.info("Data Rate: %s" % sensor.data_rate)
                    self.interface_kit.setSensorChangeTrigger(i, sensor.change)
                    self.interface_kit.setDataRate(i, sensor.data_rate)
            except PhidgetException as e:
                self.logger.exception(e)
