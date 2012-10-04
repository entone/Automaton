import gevent
import zmq.green as zmq
import settings
import simplejson as json
import util
import base64
from util import aes
from util.pubsub import PubSub
from util.rpc import RPC
from util.jsontools import ComplexEncoder
from loggers import Logger


class Manager(object):
    nodes = dict()

    def __init__(self):
        self.nodes = dict()
        self.clients_pubsub = PubSub(self, pub_port=settings.CLIENT_SUB, sub_port=settings.CLIENT_PUB, broadcast=False)
        self.nodes_pubsub = PubSub(self, pub_port=settings.NODE_SUB, sub_port=settings.NODE_PUB, parse_message=self.parse_message)
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        Logger(self)
        self.run()

    def add_node(self, obj, **kwargs):
        rpc_port = settings.NODE_RPC+len(self.nodes.keys())
        key = aes.generate_key()
        n = Node(obj=obj, address=obj.get('address'), port=rpc_port, pubsub=self.nodes_pubsub, key=key)
        self.nodes[n.name] = n
        n.publish(method='initialize_rpc', message=dict(port=rpc_port, key=base64.urlsafe_b64encode(key)), key=settings.KEY)
        return True

    def run(self):
        rpc = zmq.Context()
        rpc_socket = rpc.socket(zmq.REP)
        rpc_socket.bind("tcp://127.0.0.1:%s" % settings.CLIENT_RPC)
        self.logger.info("RPC listening on: %s" % settings.CLIENT_RPC)
        while True: 
            try:       
                message = rpc_socket.recv()
                self.logger.info("RPC Got: %s" % message)
                message = aes.decrypt(message, settings.KEY)
                ob = json.loads(message)
                res = getattr(self, ob.get("method"))(ob)
                self.logger.info("Result: %s" % res)
                st = json.dumps(res, cls=ComplexEncoder)
                st = aes.encrypt(st, settings.KEY)
                self.logger.info("Result: %s" % st)
                rpc_socket.send(st)
            except Exception as e:
                rpc_socket.send("{'error':true}")
                self.logger.exception(e)
            gevent.sleep(.1)


    def get_node(self, name):
        return self.nodes.get(name)

    def initialized(self, obj, **kwargs):
        node = self.get_node(obj.get('name'))
        if node: return node.call(method='hello')

    def get_nodes(self, obj):
        return [n.call('json') for k,n in self.nodes.iteritems()]

    def get_sensor_values(self):
        res = dict()
        for k, n in self.nodes.iteritems():
            res[k] = n.call('get_sensor_values')

        return res

    def node_change(self, obj):
        mes = json.dumps(obj, cls=ComplexEncoder)
        mes = aes.encrypt(mes, settings.KEY)
        self.clients_pubsub.publish(mes)
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

    def __init__(self, obj, address, port, pubsub, key):
        self.port = port
        self.address = address
        self.pubsub = pubsub
        self.key = key
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.obj = obj
        for k,v in obj.iteritems(): setattr(self, k, v)

    def publish(self, method, message=None, key=None):
        key = key if key else self.key
        message = message if message else {}
        message['method'] = method
        self.logger.info("Publishing: %s" % message)
        message = json.dumps(message, cls=ComplexEncoder, encoding='utf-8')
        message = aes.encrypt(message, key)
        st = self.name+message
        self.pubsub.publish(st)
        return True

    def call(self, method, message=None):
        r = RPC(address=self.address, port=self.port)
        message = message if message else {}
        message['name'] = self.name
        message['method']=  method
        resp = r.send(message, self.key)
        self.logger.info("Response: %s" % resp)
        return resp

    def parse_message(self, message):
        return aes.decrypt(message, self.key)
