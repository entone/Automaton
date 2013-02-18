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
            if image.count():
                image = settings.TIMELAPSE_URL+image[0].get('filename')
                n.webcam = image
            avgs = self.get_sensor_averages(n)
            for sensor in n.sensors:
                t = sensor._get('type')()
                self.logger.info(t)
                sensor.type = t.type
                q = dict(
                    node=n.id,
                    sensor=sensor.id,
                )
                res = node.SensorValue.find(q, as_dict=True).sort('_id', -1).limit(1)
                if res.count():
                    sensor.value = "%.2f" % res[0].get('value')
                else:
                    sensor.value = 0
        return self.default_response("dashboard.html", image=image, averages=json.dumps(avgs, cls=ComplexEncoder))

    def get_sensor_averages(self, nod):
        time = datetime.datetime.utcnow()-datetime.timedelta(days=14)
        match = {"$match":{"node":nod.id, "timestamp":{"$gte":time}, "sensor":{"$ne":"marker"}}}
        project = {
            "$project":{
                "sensor":1,
                "value":1,
                "_id":0,
                "timestamp":1,
                "day":{ 
                    "year":{"$year":"$timestamp"}, 
                    "month":{"$month":"$timestamp"}, 
                    "day":{"$dayOfMonth":"$timestamp"},
                }
            }
        }
        group1 = {
            "$group":{
                "_id":{
                    "sensor":"$sensor",
                    "day":"$day"
                },
                "average":{
                    "$avg":"$value"
                }
            }
        }
        ret = node.SensorValue._connection().aggregate([match, project, group1])
        result = {}
        for i in ret['result']:
            i['date'] = datetime.datetime(year=i['_id']['day']['year'], month=i['_id']['day']['month'], day=i['_id']['day']['day'])
            result.setdefault(i['_id']['sensor'], []).append([i['date'], i['average']])
        self.logger.info(result)

        return result
            



