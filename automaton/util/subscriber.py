import datetime
import zmq.green as zmq
import simplejson as json
import gevent
import settings

class Subscriber(object):

    running = True

    def __init__(self, callback, port=5555, filter="", spawn=True, **kwargs):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://*:%s" % port)
        self.socket.setsockopt(zmq.SUBSCRIBE, filter)
        self.callback = callback
        self.kwargs = kwargs
        self.logger = settings.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        if spawn: gevent.spawn(self.run)
    	else: self.run()

    def run(self):
        while self.running:
            st = self.socket.recv()
            ob = json.loads(st)
            ob['timestamp'] = datetime.datetime.utcnow()
            if not self.callback(ob, **self.kwargs): self.stop()
            gevent.sleep(.1)

        self.context.destroy()
        return


    def stop(self):
        self.running = False