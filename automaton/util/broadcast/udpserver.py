import gevent
from gevent import socket
from gevent.select import select
from automaton.util.event import EventDispatcher, Event
import logging
import simplejson as json

class UDPServer(EventDispatcher):

    def __init__(self, address='<broadcast>', port=5007, spawn=True, filter=None):
        super(UDPServer, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
        self.sock.bind((address, port))
        self.filter = filter
        if spawn: gevent.spawn(self.run)

    def run(self):
        self.running = True
        while self.running:
            try:
                result = select([self.sock],[],[])
                for s in result[0]:
                    msg, address = s.recvfrom(1048576)
                    self.logger.debug("Got: %s" % msg)
                    if self.filter and msg.startswith(self.filter): 
                        msg = msg[len(self.filter):]
                    elif self.filter: continue
                    self.handle(msg, address)
                gevent.sleep(0)
            except Exception as e:
                self.logger.exception(e)

    def close(self):
        self.running = False
        self.sock.close()

    def encrypt(self, message):
        return message

    def decrypt(self, message):
        return message

    def handle(self, msg, address):
        msg = self.decrypt(msg)
        msg = json.loads(msg)
        self.logger.debug("MSG: %s" % msg)
        try:
            self.fire(message=msg, address=address)
            res = getattr(self, msg.get('method'))(msg, address)            
        except Exception as e:
            self.logger.exception(e)

    def sendto(self, message, address):
        self.sock.sendto(self.encrypt(message), address)

    def broadcast(self, message):
        self.sock.sendto(self.encrypt(message), ('<broadcast>', self.port))

    def rpc(self, message, address):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
        sock.sendto(self.encrypt(message), address)
        while True:
            self.logger.info("waiting...")
            result = select([sock],[],[])
            for s in result[0]:
                msg, address = s.recvfrom(1048576)
                self.logger.info(msg)
                msg = self.decrypt(msg)
                msg = json.loads(msg)
                sock.close()
                self.sock.close()
                return msg

            gevent.sleep(0)
