import simplejson as json
import aes
from automaton.util.jsontools import ComplexEncoder
from automaton import settings
from automaton import util

class RPC(object):

    port = 6666

    def __init__(self, address='*', port=6666):
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://%s:%s" % (address, port))     

    def send(self, ob, key):
        self.logger.info("Calling: %s" % ob)
        st = aes.encrypt(json.dumps(ob, cls=ComplexEncoder), key)
        self.socket.send(st)
        res = self.socket.recv()
        res = aes.decrypt(res, key)
        self.socket.close()
        self.context.destroy()
        return json.loads(res)
        

    
