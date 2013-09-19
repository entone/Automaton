from ctypes import *
import sys
import random
import logging
import base64
import gevent
import sqlite3
import simplejson as json
from gevent import socket
from gevent.select import select
from automaton.util.jsontools import ComplexEncoder
from automaton.util import aes
from automaton.util.broadcast.udpserver import UDPServer
from automaton.loggers import Logger
from automaton import settings
from automaton.node.arduino import Arduino


class Node(UDPServer):

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
        super(Node, self).__init__(filter=self.name)
        self.webcam = kwargs.get('webcam', '')
        self.initializing = True
        self.manager = None
        self.logger = logging.getLogger(__name__)
        self.initialize()
        self.interface_kit = Arduino(self.sensors)
        while True: gevent.sleep(0)

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
        while self.initializing:            
            self.logger.info("Waiting for manager")
            json = dict(method='add_node')
            self.publish(json)
            gevent.sleep(1)
        return

    def initialize_rpc(self, message, address):
        settings.KEY = base64.urlsafe_b64decode(str(message.get('key')))
        self.initializing = False
        self.publish(dict(method='initialized'))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
        sock.bind(('', message.get('port')))
        while True:
            self.logger.info("Waiting for message")
            result = select([sock],[],[])
            for s in result[0]:
                msg, address = s.recvfrom(1048576)
                msg = self.decrypt(msg)
                msg = json.loads(msg)
                try:
                    res = getattr(self, msg.get("method"))(msg)
                    sock.sendto(self.encrypt(res), address)
                except Exception as e:
                    self.logger.exception(e)
            gevent.sleep(0)

    def encrypt(self, message):
        return aes.encrypt(json.dumps(message, cls=ComplexEncoder), settings.KEY)

    def decrypt(self, message):
        return aes.decrypt(message, settings.KEY)

    def publish(self, message):
        message['name'] = self.name
        message['node_id'] = self.id
        message['method'] = message.get('method', 'node_change')
        self.logger.info("Publishing: %s" % message)
        self.broadcast(message)
        self.test_triggers(message)

    def test_triggers(self, message):
        for t in self.triggers:
            t.handle_event(message)

    def set_id(self, message):
        c = self.db.cursor()
        c.execute("INSERT INTO node_registration VALUES (?)", (message.get('id'),))
        self.db.commit()
        c.close()
        return True

    def hello(self, obj):
        o = self.json()
        self.logger.info("Hello: %s" % o)
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
