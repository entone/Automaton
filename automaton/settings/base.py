import os 
import sys
import logging
from logging.handlers import SysLogHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

TEMPLATE_DIRS = ["%s/templates/" % PROJECT_DIR,]

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.DEBUG

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)

def get_logger(name):
	logger = logging.getLogger(name)
	handler = SysLogHandler(address='/dev/log')
	logger.addHandler(handler)
	return logger



