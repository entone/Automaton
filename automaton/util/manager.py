import gevent
import zmq.green as zmq
from util.pubsub import PubSub
from util.rpc import RPC
import settings
import simplejson as json
from util.jsontools import ComplexEncoder
import util

class Manager(object):
    nodes = dict()

    def __init__(self):
        self.nodes = dict()
        self.clients_pubsub = PubSub(self, pub_port=settings.CLIENT_SUB, sub_port=settings.CLIENT_PUB, broadcast=False)
        self.nodes_pubsub = PubSub(self, pub_port=settings.NODE_SUB, sub_port=settings.NODE_PUB)
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.run()

    def add_node(self, obj, **kwargs):
        rpc_port = settings.NODE_RPC+len(self.nodes.keys())
        n = Node(obj, rpc_port, self.nodes_pubsub)
        self.nodes[n.name] = n
        n.publish(method='initialize_rpc', message=dict(port=rpc_port))
        return True

    def run(self):
        while True:
            rpc = zmq.Context()
            rpc_socket = rpc.socket(zmq.REP)
            rpc_socket.bind("tcp://*:%s" % settings.CLIENT_RPC)
            self.logger.info("RPC listening on: %s" % settings.CLIENT_RPC)
            while True:
                message = rpc_socket.recv()
                ob = json.loads(message)
                try:
                    res = getattr(self, ob.get("method"))(ob)
                    st = json.dumps(res, cls=ComplexEncoder)
                    rpc_socket.send(st)
                except Exception as e:
                    self.logger.exception(e)
                gevent.sleep(.1)

    def get_node(self, name):
        return self.nodes.get(name)

    def initialized(self, obj, **kwargs):
        node = self.get_node(obj.get('name'))
        if node: return node.call(method='hello')

    def get_nodes(self, obj):
        return [n.obj for k,n in self.nodes.iteritems()]

    def node_change(self, obj):
        self.clients_pubsub.publish(json.dumps(obj, cls=ComplexEncoder))
        return True

    def set_output_state(self, obj):
        node = self.get_node(obj.get('node'))
        res = node.call('set_output_state', obj)



class Node(object):

    def __init__(self, obj, port, pubsub):
        self.port = port
        self.pubsub = pubsub
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.obj = obj
        for k,v in obj.iteritems(): setattr(self, k, v)

    def publish(self, method, message=None):
        message['method'] = method
        message = message if message else {}
        st = "%s%s" % (self.name, json.dumps(message, cls=ComplexEncoder))
        self.pubsub.publish(st)
        return True

    def call(self, method, message=None):
        r = RPC(port=self.port)
        message = message if message else {}
        message['name'] = self.name
        message['method']=  method
        resp = r.send(message)
        self.logger.info("Response: %s" % resp)
        r.done()
        return resp