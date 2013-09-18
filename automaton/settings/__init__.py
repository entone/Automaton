import os
from base import *

try:
    env = os.environ['ENVY_ENV']    
    if env == 'dev': from dev import *
    if env == 'test': from test import *
    if env == 'staging': from staging import *
    if env == 'production': from production import *
except Exception as e:pass