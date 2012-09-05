import json
import zmq.green as zmq
from util.jsontools import ComplexEncoder

LIVE = True

try:
    import Phidgets
except Exception as e:
    LIVE = False

class RPC(object):

    def __init__(self, uri):
    	if LIVE:
        	con = zmq.Context()
        	self.socket = con.socket(zmq.REQ)
        	self.socket.connect(uri)

    def send(self, ob):
    	print "Setting: %s" % ob
    	if LIVE:
        	st = json.dumps(ob, cls=ComplexEncoder)
        	self.socket.send(st)
        	res = self.socket.recv()
        	return json.loads(res)

        return {}
    
