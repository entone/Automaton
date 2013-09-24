import gevent
import sqlite3
import datetime
import simplejson as json
import base64
import logging
from gevent import socket
from gevent.select import select
from automaton import settings
from automaton.util.broadcast import BroadcastClient, BroadcastServer
from automaton.util.rpc import RPCClient, RPCServer
from automaton.util import aes
from automaton.util.jsontools import ComplexEncoder
#from automaton.util.cloud import Cloud
#from automaton.util.download_image import DownloadImage
#from automaton.loggers import Logger, CloudLogger


class Manager(object):
    nodes = dict()

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.nodes = dict()
        self.node_server = BroadcastServer(port=settings.NODE_SUB, key=settings.KEY)
        self.node_server.decrypt = self.node_decrypt
        self.node_server.check_filter = self.node_filters
        #self.node_server+= self.node_change
        self.node_server+= self.rpc_callback
        self.rpc_server = RPCServer(address='', port=settings.CLIENT_RPC, key=settings.KEY, callback=self.rpc_callback)
        self.clients = BroadcastClient(port=settings.CLIENT_SUB, key=settings.KEY)
        #self.cloud = Cloud()
        #self.register()        
        #Logger(self)
        #CloudLogger(self)
        self.running = True
        while self.running: gevent.sleep(1)

    def node_filters(self, message):
        for k,n in self.nodes.iteritems():
            if n.name and message.startswith(n.name):
                return message[len(n.name):]

        return message

    def node_decrypt(self, message):
        for k,n in self.nodes.iteritems():
            try:
                return json.loads(aes.decrypt(message, n.key))
            except Exception as e:
                self.logger.exception(e)
        try:
            return json.loads(aes.decrypt(message, settings.KEY))
        except Exception as e:
            self.logger.exception(e)
            return json.loads(message)

    def rpc_callback(self, message, address):
        return getattr(self, message.get("method"))(message, address)

    def register(self):
        self.db = sqlite3.connect("automaton.db", detect_types=sqlite3.PARSE_DECLTYPES)
        c = self.db.cursor()
        try:
            c.execute('''CREATE TABLE registration (id text)''')
        except Exception as e: pass
        self.logger.info("Table Created")
        c.execute("SELECT id FROM registration")
        self.id = c.fetchone()
        self.logger.info(self.id)     
        if not self.id:
            res = self.cloud.register_location()
            c.execute("INSERT INTO registration VALUES (?)", (res.get('id'),))
            self.id = res.get('id')
            self.db.commit()
            self.logger.info(self.id)
        else:
            self.id = self.id[0]

        c.close()

    def add_node(self, obj, address, **kwargs):
        rpc_port = settings.NODE_RPC+len(self.nodes.keys())
        key = aes.generate_key()
        n = Node(name=obj.get('name'), address=address, port=rpc_port, key=key)
        self.nodes[n.name] = n
        n.publish(method='initialize_rpc', message=dict(port=rpc_port, key=base64.urlsafe_b64encode(key)), key=settings.KEY, add_filter=False)
        return True

    def get_node(self, name):
        return self.nodes.get(name)

    def initialized(self, obj, address, **kwargs):
        self.logger.debug("initialized!")
        node = self.get_node(obj.get('name'))
        if node:
            gevent.sleep(2)
            obj = node.call(method='hello')
            node.set_obj(obj)  
            #if not obj.get('id'):
                #obj['location_id'] = self.id
                #res = self.cloud.add_node(obj)
                #self.logger.info(res)
                #mes = dict(id=res.get('id'))
                #node.id = res.get('id')
                #success = node.call(method='set_id', message=mes)

            #node.downloader = DownloadImage(node.id, "%s%s" % (node.webcam, settings.TIMELAPSE_PATH), settings.TIMELAPSE_SAVE_PATH, settings.TIMELAPSE_PERIOD, s3=True, cb=self.log_image)

        return True

    def log_image(self, filename, id):
        ts = datetime.datetime.utcnow()
        #self.cloud.save_image(dict(timestamp=ts, location=self.id, node=id, filename=filename))

    def get_nodes(self, obj, address):
        obj = [n.call('json') for k,n in self.nodes.iteritems()]
        self.logger.debug("NODES: %s" % obj)
        return obj

    def get_sensor_values(self):
        res = dict(location_id=self.id, nodes=[])
        for k, n in self.nodes.iteritems():
            res['nodes'].append(n.call('get_sensor_values'))

        return res

    def node_change(self, message, address):
        #obj['location_id'] = self.id
        self.logger.info("Node Change: %s" % message)
        self.clients.publish(message, close=False)
        return True

    def set_output_state(self, obj):
        node = self.get_node(obj.get('node'))
        res = node.call('set_output_state', obj)

    def parse_message(self, message):
        for k,n in self.nodes.iteritems():
            try:
                return n.parse_message(message)
            except Exception as e:
                self.logger.exception(e)

        try:
            return aes.decrypt(message, settings.KEY)
        except Exception as e:
            self.logger.exception(e)
            return message



class Node(object):

    def __init__(self, name, address, port, key):
        self.name = name
        self.port = port
        self.address = address        
        self.key = key
        self.id = None
        self.logger = logging.getLogger(__name__)

    def set_obj(self, obj):
        self.obj = obj
        for k,v in obj.iteritems(): setattr(self, k, v)

    def publish(self, method, message=None, key=None, add_filter=True):
        key = key if key else self.key
        message = message if message else {}
        message['method'] = method
        self.logger.debug("Publishing: %s" % message)
        client = BroadcastClient(port=settings.NODE_SUB, filter=self.name, key=key)
        client.publish(message, add_filter=add_filter)
        return True

    def call(self, method, message=None):
        message = message if message else {}
        message['name'] = self.name
        message['method']=  method
        self.logger.info("Calling: %s" % message)
        self.logger.info("Address: %s" % self.address[0])
        self.logger.info("Port: %s" % self.port)
        rpc = RPCClient(self.address[0], self.port, self.key)
        return rpc.send(message)
