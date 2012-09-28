import simplejson as json
import zmq.green as zmq
from util.jsontools import ComplexEncoder
import settings
import util

class RPC(object):

    port = 6666

    def __init__(self, port=6666):
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://*:%s" % port)        

    def send(self, ob):
        print "Calling: %s" % ob
        st = json.dumps(ob, cls=ComplexEncoder)
        self.socket.send(st)
        res = self.socket.recv()
        return json.loads(res)

    def done(self):
        self.context.destroy()

    
