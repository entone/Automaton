import gevent
import zmq.green as zmq
import json
from util.jsontools import ComplexEncoder

class Publisher(object):

    def __init__(self, uri):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(uri)
        gevent.spawn(self.run)

    def publish(self, dic):
        st = "%s" % json.dumps(dic, cls=ComplexEncoder)
        self.socket.send(st)

    #override this
    def run(self): pass

