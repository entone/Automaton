import datetime
import zmq.green as zmq
import json
import gevent

class Subscriber(object):

    def __init__(self, callback, port=5555, filter="", spawn=True, **kwargs):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://*:%s" % port)
        self.socket.setsockopt(zmq.SUBSCRIBE, filter)
        self.callback = callback
        self.kwargs = kwargs
        if spawn: gevent.spawn(self.run)
    	else: self.run()

    def run(self):
        while True:
            st = self.socket.recv()
            ob = json.loads(st)
            ob['timestamp'] = datetime.datetime.utcnow()
            self.callback(ob, **self.kwargs)
            gevent.sleep(.1)
