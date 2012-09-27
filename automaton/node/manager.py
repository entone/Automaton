from util.pubsub import PubSub
import settings

class Manager(object):
    node_filters = []

    def __init__(self):
        self.node_filters = []
        self.nodes = PubSub(self, pub_port=settings.NODE_SUB, sub_port=settings.NODE_PUB)
        self.clients = PubSub(self, pub_port=settings.CLIENT_SUB, sub_port=settings.CLIENT_PUB)
        self.logger = settings.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))

    def add_node(self, obj):
        self.node_filters.append(obj.get('name'))
        return True


