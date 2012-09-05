import json
import zmq.green as zmq
from util.jsontools import ComplexEncoder

class RPC(object):

    port = 6666

    def __init__(self, port=6666):
        con = zmq.Context()
        self.socket = con.socket(zmq.REQ)
        self.socket.connect("tcp://*:%s" % port)

    def send(self, ob):
        print "Calling: %s" % ob
        st = json.dumps(ob, cls=ComplexEncoder)
        self.socket.send(st)
        res = self.socket.recv()
        return json.loads(res)
    
