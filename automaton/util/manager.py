import gevent
from util.pubsub import PubSub
import settings

class Manager(object):
    node_filters = []

    def __init__(self):
        self.node_filters = []        
        self.clients = PubSub(self, pub_port=settings.CLIENT_SUB, sub_port=settings.CLIENT_PUB)
        self.nodes = PubSub(self, pub_port=settings.NODE_SUB, sub_port=settings.NODE_PUB)
        self.logger = settings.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.run()

    def add_node(self, obj):
    	rpc_port = settings.NODE_RPC+len(self.node_filters)
        self.node_filters.append(dict(name=name, port=rpc_port))
        self.publish(settings.NODE_RPC)

    def run(self):
    	while True: 
    		gevent.sleep(5)
    		self.nodes.publish(dict(test="Woot", method="json"))


