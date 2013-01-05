import gevent
import random
import datetime
import simplejson as json
import settings
import util
import models.node as node
from controllers import DefaultController
from envy.response import Response
from util.jsontools import ComplexEncoder
from util.subscriber import Subscriber
from util.rpc import RPC
from util.decorators import level

class Dashboard(DefaultController):

    @level(0)
    def index(self):
        home = self.request.env.get('HTTP_HOST')
        self.logger.info("Nodes: %s" % self.session.location.nodes)        
        for n in self.session.location.nodes:
            self.logger.warn("N: %s" % len(n.sensors))
            i_q = dict(node=n.id)
            image = node.Image.find(i_q, as_dict=True, fields={'filename':1}).sort('_id', -1).limit(1)
            self.logger.warn("Image: %s" % image.count())
            if image.count():
                image = settings.TIMELAPSE_URL+image[0].get('filename')
                self.logger.warn("Image: %s" % image)
                n.webcam = image
            for sensor in n.sensors:
                t = sensor._get('type')()
                self.logger.info(t)
                sensor.type = t.type
                q = dict(
                    node=n.id,
                    sensor=sensor.id,
                )
                self.logger.info(q)
                res = node.SensorValue.find(q, as_dict=True).sort('_id', -1).limit(1)
                if res.count():
                    self.logger.info(res[0])
                    sensor.value = "%.2f" % res[0].get('value')
                else:
                    sensor.value = 0
        return self.default_response("dashboard.html", image=image)
