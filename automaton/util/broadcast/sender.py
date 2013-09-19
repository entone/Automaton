import gevent
from gevent import socket

port = 5007
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)

sock.sendto("testing", ('<broadcast>', port))