import gevent
import simplejson as json
from gevent import socket
from gevent.select import select
from automaton import settings
from automaton.util.jsontools import ComplexEncoder
from automaton.util import aes
import logging

class RPC(object):

    def __init__(self, address, port, key):
        self.logger = logging.getLogger(__name__)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
        self.address = (address, port)
        self.key = key

    def encrypt(self, message):
        return aes.encrypt(json.dumps(message, cls=ComplexEncoder), self.key)

    def decrypt(self, message):
        return json.loads(aes.decrypt(message, self.key))        

class RPCClient(RPC):

    def send(self, message):
        msg = self.encrypt(message)
        self.sock.sendto(msg, self.address)
        while True:
            self.logger.debug("Waiting for result")
            result = select([self.sock],[],[])
            for s in result[0]:
                msg, address = s.recvfrom(1048576)                
                msg = self.decrypt(msg)
                self.logger.debug("Got Result: %s" % msg)
                self.sock.close()
                return msg

class RPCServer(RPC):

    def __init__(self, address, port, key, callback):
        super(RPCServer, self).__init__(address, port, key)        
        self.running = True
        self.callback = callback
        gevent.spawn(self.run)

    def run(self):
        self.sock.bind(self.address)
        while True:
            self.logger.debug("Waiting for message")
            result = select([self.sock],[],[])
            for s in result[0]:
                msg, address = s.recvfrom(1048576)
                msg = self.decrypt(msg)
                try:
                    res = self.callback(msg, address)
                    self.logger.debug("GOT RPC RESULT: %s" % res)
                    self.sock.sendto(self.encrypt(res), address)
                except Exception as e:
                    self.logger.exception(e)
            gevent.sleep(0)
        

    
