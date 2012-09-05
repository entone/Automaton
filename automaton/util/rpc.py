import json
import zmq.green as zmq
from util.jsontools import ComplexEncoder

LIVE = True

try:
    import Phidgets
except Exception as e:
    LIVE = False

class RPC(object):

    port = 6666

    def __init__(self, port=6666):
    	if LIVE:
        	con = zmq.Context()
        	self.socket = con.socket(zmq.REQ)
        	self.socket.connect("tcp://*:%s" % port)

    def send(self, ob):
    	print "Setting: %s" % ob
    	if LIVE:
        	st = json.dumps(ob, cls=ComplexEncoder)
        	self.socket.send(st)
        	res = self.socket.recv()
        	return json.loads(res)

        return {}
    
