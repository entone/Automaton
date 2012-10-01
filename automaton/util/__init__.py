from optparse import OptionParser
import logging
from logging.handlers import SysLogHandler
import socket
import fcntl
import struct
import settings
import sys

def get_ip_address(ifname):
    ip = socket.gethostbyname(socket.gethostname())
    if not ip.startswith('127'): return ip
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def get_interface_option():
	usage = "usage: %prog [options] arg"
	parser = OptionParser(usage)
	parser.add_option('-i', '--interface', dest='interface', help='What network interface to broadcast on, default=eth0')
	(options, args) = parser.parse_args()

	print options
	if options.interface:
		settings.NETWORK_INTERFACE = options.interface

	settings.IP_ADDRESS = get_ip_address(settings.NETWORK_INTERFACE)

	print settings.IP_ADDRESS

def get_logger(name):
    if sys.platform == "darwin":
        address = "/var/run/syslog"
    else:
        address = '/dev/log'
    logger = logging.getLogger(name)
    handler = SysLogHandler(address=address)
    logger.addHandler(handler)
    return logger