import datetime
import zmq.green as zmq
import simplejson as json
import gevent
import util
import settings
import select
import socket
from gevent.monkey import patch_all
patch_all()

class Subscriber(object):

    running = True

    def __init__(self, callback, port, filter="", spawn=True, broadcast=True, **kwargs):
        self.filter = filter
        self.callback = callback
        self.kwargs = kwargs
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.logger.info("Subscriber: %s"%port)

        if broadcast:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(('<broadcast>', port))
            self.sock.setblocking(0)
            runner = self.run_udp
        else:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.SUB)
            self.socket.connect("tcp://*:%s" % port)
            self.socket.setsockopt(zmq.SUBSCRIBE, filter)
            runner = self.run

        if spawn: gevent.spawn(runner)
        else: runner()

    def handle_message(self, message, address=['*']):
        if self.filter and message.startswith(self.filter): message = message[len(self.filter):]
        ob = json.loads(message)
        ob['address'] = address[0]
        ob['timestamp'] = datetime.datetime.utcnow()
        if not self.callback(ob, **self.kwargs): self.stop()

    def run_udp(self):
        while self.running:
            self.logger.info("Waiting for message")
            result = select.select([self.sock],[],[])
            msg, address = result[0][0].recvfrom(1048576) 
            self.handle_message(msg, address)
            gevent.sleep(.1)

        self.sock.close()

    def run(self):
        while self.running:
            self.logger.info("Waiting for message")
            st = self.socket.recv()
            self.handle_message(st)
            gevent.sleep(.1)

        self.context.destroy()
        return


    def stop(self):
        self.running = False
