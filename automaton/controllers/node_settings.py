import datetime
import simplejson as json
import settings
import util
import models.node as node
from controllers import DefaultController
from envy.response import Response
from util.jsontools import ComplexEncoder
from util.decorators import level

class NodeSettings(DefaultController):

    @level(0)
    def index(self):
        return self.default_response("settings.html")