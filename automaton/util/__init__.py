from optparse import OptionParser
import logging
from logging.handlers import SysLogHandler
import socket
import fcntl
import struct
import settings
import sys
import re
import unidecode
import hashlib
import random

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

def slugify(str):
    str = unidecode.unidecode(str).lower()
    return re.sub(r'\W+','-',str)

def encrypt_password(self, password, salt=False):
    algo="sha1"
    lib = hashlib.__getattribute__(algo)
    salt = salt if salt else lib(str(random.random())).hexdigest()[:5]
    hash = lib("%s%s"%(salt, password)).hexdigest()
    return "%s$%s$%s" % (algo, salt, hash)
        
def check_password(self, password, encrypted):
    try:
        algo, salt, hash = str(encrypted).split("$")
        return encrypted == encrypt_password(password, salt)
    except Exception as e: 
        self.logger.exception(e)
        return False