from optparse import OptionParser
import logging
from logging.handlers import SysLogHandler
import socket
import fcntl
import struct
from automaton import settings
import sys
import re
import unidecode
import hashlib
import random
import json
from util import aes

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

def slugify(st):
    st = unidecode.unidecode(unicode(st)).lower()
    return re.sub(r'\W+','-',st)

def encrypt_password(password, salt=False):
    algo="sha1"
    lib = hashlib.__getattribute__(algo)
    salt = salt if salt else lib(str(random.random())).hexdigest()[:5]
    hash = lib("%s%s"%(salt, password)).hexdigest()
    return "%s$%s$%s" % (algo, salt, hash)
        
def check_password(password, encrypted):
    try:
        algo, salt, hash = str(encrypted).split("$")
        enc = encrypt_password(password, salt)
        print enc
        return encrypted == enc
    except Exception as e: 
        self.logger.exception(e)
        return False

def get_request_payload(request, is_json=True, encrypted=False, key=None):
    post = request.env['wsgi.input'].read(10485760)
    print post
    if encrypted:
        key = key if key else settings.KEY
        post = aes.decrypt(post, key)
    if is_json:
        post = json.loads(post)
    
    return post
