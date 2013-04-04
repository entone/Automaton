import gevent
import os
import random
import datetime
import simplejson as json
import settings
import util
import models.node as node
from envy.controller import Controller
from controllers import DefaultController
from envy.response import Response
from util.jsontools import ComplexEncoder
from util.rpc import RPC
from util.decorators import level

class Calibrate(DefaultController):

    @level(0)
    def index(self):
        return self.default_response("calibrate.html")

    def calibrate(self, node_id, type):
        return Response(json.dumps(dict(result="woot"), cls=ComplexEncoder))