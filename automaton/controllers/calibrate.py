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

    def calibrate(self, node, type):
    	rpc = RPC(port=settings.CLIENT_RPC)
    	mes = dict(node=node, type=type, method='calibrate')
        res = rpc.send(mes, settings.KEY)
        return Response(json.dumps(res, cls=ComplexEncoder))