import gevent
from gevent import socket
from gevent.select import select
from automaton.util.event import EventDispatcher
import logging
import simplejson as json
from automaton.util import aes
from automaton.util.jsontools import ComplexEncoder

class Broadcast(EventDispatcher):

    def __init__(self, address='<broadcast>', port=5007, filter=None, key=None):
        super(Broadcast, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.address = address
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)        
        self.key = key
        self.filter = filter

    def encrypt(self, message):
        return aes.encrypt(json.dumps(message, cls=ComplexEncoder), self.key)

    def decrypt(self, message):
        return json.loads(aes.decrypt(message, self.key))

class BroadcastClient(Broadcast):

    def publish(self, message, close=True, add_filter=True):
        self.logger.debug("sending: %s" % message)
        msg = self.encrypt(message)
        msg = self.filter+msg if self.filter and add_filter else msg
        self.sock.sendto(msg, (self.address, self.port))
        if close: self.sock.close()

class BroadcastServer(Broadcast, EventDispatcher):

    def __init__(self, address='<broadcast>', port=5007, filter=None, key=None):
        super(BroadcastServer, self).__init__(address, port, filter, key)
        gevent.spawn(self.run)
        self.running = True        

    def check_filter(self, msg):
        if self.filter and msg.startswith(self.filter): 
            return msg[len(self.filter):]
        elif self.filter: return None

        return msg

    def run(self):
        self.sock.bind((self.address, self.port))
        while self.running:
            try:
                result = select([self.sock],[],[])
                for s in result[0]:
                    msg, address = s.recvfrom(1048576)
                    self.logger.debug("Got: %s" % msg)
                    msg = self.check_filter(msg)
                    if not msg: continue
                    self.handle(msg, address)
                gevent.sleep(0)
            except Exception as e:
                self.logger.exception(e)

    def close(self):
        self.running = False
        self.sock.close()

    def handle(self, msg, address):
        msg = self.decrypt(msg)
        self.logger.debug("MSG: %s" % msg)
        try:
            self.fire(message=msg, address=address)
        except Exception as e:
            self.logger.exception(e)

    