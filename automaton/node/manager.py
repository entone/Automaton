from util.publisher import Publisher
from util.subscriber import Subscriber

class Manager(Publisher):
    base_port = 5555
    nodes = []

    def __init__(self, nodes, *args, **kwargs):
        for node in nodes:
            pub = self.base_port+1
            rpc = self.base_port+2
            name = "Test-%s" % pub
            print "Starting Node: %s" % name
            n = node(name, publisher=pub, rpc=rpc)
            n.subscriber = Subscriber(self.handle_message, port=pub)
            self.nodes.append(n)
            self.base_port = rpc

        super(Manager, self).__init__(*args, spawn=False, **kwargs)

    def get_nodes(self, ob):
        return [n.json() for n in self.nodes]


    def get_node(self, name):
        for n in self.nodes:
            if n.name == name: return n

    def __getattr__(self, key):
        def func(ob):
            node = self.get_node(ob.get('node'))
            if node:
                try:
                    getattr(node, ob.get('method'))(ob)
                except Exception as e:
                    print e

        return func

    def handle_message(self, ob):
        self.publish(ob)


