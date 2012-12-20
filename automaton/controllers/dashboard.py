import gevent
import random
import datetime
import simplejson as json
import settings
import util
import models.node as node
from envy.controller import Controller
from envy.response import Response
from util.jsontools import ComplexEncoder
from util.subscriber import Subscriber
from util.rpc import RPC
from util.decorators import level

loc_id = "50ccfc511f99cd16ea70c3ea"

class Dashboard(Controller):

    @level(1)
    def index(self):
        location = node.Location(id=loc_id)
        self.logger.debug("Got location: %s" % len(location.nodes))
        home = self.request.env.get('HTTP_HOST')
        for n in location.nodes:
            for sensor in n.sensors:
                t = sensor._get('type')()
                sensor.type = t.type
                q = dict(
                    node=n.id,
                    sensor=sensor.id,
                )
                res = node.SensorValue.find(q, as_dict=True).sort('_id', -1).limit(1)
                self.logger.info(res[0])
                sensor.value = res[0].get('value')
        return Response(self.render("dashboard.html", values=json.dumps(location.json(), cls=ComplexEncoder), location=location, url=home, settings=settings, session=self.session))
