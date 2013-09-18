import gevent
import zmq.green as zmq
import simplejson as json
from util.jsontools import ComplexEncoder
from automaton import settings
import util

class Publisher(object):

    def __init__(self, publisher=5555, rpc=6666, spawn=True, connect=True):
        if connect:
            self.publisher = zmq.Context()
            self.publisher_socket = self.publisher.socket(zmq.PUB)
            self.publisher_socket.bind("tcp://*:%s" % publisher)
            self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
            self.logger.info("Publishing on: %s" % publisher)
            self.rpc = zmq.Context()
            self.rpc_socket = self.rpc.socket(zmq.REP)
            self.rpc_socket.bind("tcp://*:%s" % rpc)
            if spawn: gevent.spawn(self.do_run)
            else: self.do_run()

    def publish(self, dic):
        st = json.dumps(dic, cls=ComplexEncoder)
        self.logger.info("Publishing: %s" % st)
        self.publisher_socket.send(st)

    def send(self, res):
        st = json.dumps(res, cls=ComplexEncoder)
        self.rpc_socket.send(st)

    def do_run(self):
        self.run()
        while True:
            message = self.rpc_socket.recv()
            ob = json.loads(message)
            try:
                res = getattr(self, ob.get("method"))(ob)
                self.send(res)
            except Exception as e:
                self.logger.exception(e)
            gevent.sleep(.1)

    def run(self):pass

