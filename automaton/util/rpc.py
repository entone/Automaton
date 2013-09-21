import simplejson as json
from gevent import socket
from gevent.select import select
from automaton.util.jsontools import ComplexEncoder
from automaton import settings
from automaton import util
from automaton.util import aes

class RPC(object):

    def __init__(self, address, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)        
        self.address = (self.address[0], self.port)

    def send(self, message, key):
        msg = aes.encrypt(json.dumps(message, cls=ComplexEncoder), key)
        self.sock.sendto(msg, self.address)
        while True:
            result = select([self.sock],[],[])
            for s in result[0]:
                msg, address = s.recvfrom(1048576)
                msg = self.parse_message(msg)
                msg = json.loads(msg)
                self.sock.close()
                return msg
        

    
