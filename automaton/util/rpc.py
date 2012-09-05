import json
import zmq.green as zmq
from util.jsontools import ComplexEncoder

class RPC(object):

    def __init__(self, uri):
        con = zmq.Context()
        self.socket = con.socket(zmq.REQ)
        self.socket.connect(uri)

    def send(self, ob):
        st = json.dumps(ob, cls=ComplexEncoder)
        self.socket.send(st)
        res = self.socket.recv()
        return json.loads(res)
    
