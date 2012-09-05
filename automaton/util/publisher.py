import gevent
import zmq.green as zmq
import json
from util.jsontools import ComplexEncoder

class Publisher(object):

    NODE = ""
    outputs = dict()
    sensors = dict()
    inputs = dict()

    def __init__(self, publisher, rpc, node="test"):
        self.publisher = zmq.Context()
        self.publisher_socket = self.publisher.socket(zmq.PUB)
        self.publisher_socket.bind(publisher)

        self.rpc = zmq.Context()
        self.rpc_socket = self.rpc.socket(zmq.REP)
        self.rpc_socket.bind(rpc)

        self.NODE = node
        
        self.do_run()

    def publish(self, dic):
        st = json.dumps(dic, cls=ComplexEncoder)
        self.publisher_socket.send(st)

    def send(self, res):
        st = json.dumps(res, cls=ComplexEncoder)
        self.rpc_socket.send(st)

    def set_output_state(self, ob):
        output = self.outputs.get(ob.get('id'))
        if output:
            print "turning %s to %s index: %s" % (ob.get('id'), ob.get('state'), output.get('index'))
            self.interface_kit.setOutputState(output.get('index'), ob.get('state'))
            return dict(state=ob.get('state'))

    def do_run(self):
        self.run()
        while True:
            message = self.rpc_socket.recv()
            ob = json.loads(message)
            try:
                res = getattr(self, ob.get("method"))(ob)
                self.send(res)
            except Exception as e:
                print e
            gevent.sleep(.1)

