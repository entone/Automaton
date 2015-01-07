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
import sqlite3
from arduino import Arduino

class Node(object):

    name = None
    id = None
    sensors = []
    outputs = []
    inputs = []
    triggers = []
    clocks = []
    repeaters = []
    pids = []
    interface_kit = None
    webcam=None

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name', 'Node')
        self.webcam = kwargs.get('webcam', '')
        self.initializing = True
        self.manager = PubSub(self, pub_port=settings.NODE_PUB, sub_port=settings.NODE_SUB, sub_filter=self.name)
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.initialize()
        try:
            self.interface_kit = Arduino(self.sensors)
        except:pass
        self.run()

    def run(self):
        while True:
            self.set_output_state(dict(index=13, state=True))
            gevent.sleep(1)
            self.set_output_state(dict(index=13, state=False))
            gevent.sleep(1)

    def initialize(self):
        self.db = sqlite3.connect("automaton.db", detect_types=sqlite3.PARSE_DECLTYPES)
        c = self.db.cursor()
        try:
            c.execute('''CREATE TABLE node_registration (id text)''')
        except Exception as e: pass
        self.logger.info("Table Created")
        c.execute("SELECT id FROM node_registration")
        self.id = c.fetchone()
        if self.id: self.id = self.id[0]
        self.logger.info("ID: %s" % self.id)
        c.close()
        count = 0
        while self.initializing:
            if count == 30:
                self.logger.warning("Manager not responding. Moving on")
                return
            count = count+1
            self.logger.info("Waiting for manager")
            json = dict(name=self.name, method='add_node')
            self.publish(json)
            gevent.sleep(1)
        return

    def publish(self, message):
        message['name'] = self.name
        message['node_id'] = self.id
        message['method'] = message.get('method', 'node_change')
        self.logger.info("Publishing: %s" % message)
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
            gevent.sleep(0)

    def set_id(self, message):
        c = self.db.cursor()
        c.execute("INSERT INTO node_registration VALUES (?)", (message.get('id'),))
        self.db.commit()
        c.close()
        return True

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
        res = {"id":self.id}
        for sensor in self.sensors:
            res[sensor.id] = sensor.json()

        return res

    def get_output_values(self):
        res = {"id":self.id}
        for output in self.outputs:
            res[ouput.id] = output.json()

        return res

    def set_output_state(self, ob):
        output = self.get_output(ob.get('index'))
        if output:
            self.logger.info("%s: turning %s to %s index: %s" % (self.name, output.display, ob.get('state'), output.index))
            output.set_state(ob.get('state'))
            return dict(state=output.current_state)

    def digital(self, index, value):
        self.interface_kit.digital(index, value)

    def json(self, ob=None):
        return dict(
            id=self.id,
            name=self.name,
            webcam=self.webcam,
            sensors=[s.json() for s in self.sensors],
            outputs=[o.json() for o in self.outputs],
            inputs=[i.json() for i in self.inputs],
            triggers=[t.json() for t in self.triggers],
            repeaters=[r.json() for r in self.repeaters],
            clocks=[c.json() for c in self.clocks],
            pids=[p.json() for p in self.pids],
            cls=self.__class__.__name__
        )

    def __conform__(self, protocol):
        return json.dumps(self.json(), cls=ComplexEncoder)
