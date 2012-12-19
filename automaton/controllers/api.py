import gevent
import random
import datetime
import simplejson as json
import settings
import util
import models
from envy.controller import Controller
from envy.response import Response
from util.jsontools import ComplexEncoder
from util.subscriber import Subscriber
from util.rpc import RPC
from bson.objectid import ObjectId

def fill_object(o, obj, nots=None):
    for k,v in obj.iteritems():
        if not nots or not k in nots:
            try:
                setattr(o, k, v)
            except Exception as e:
                print e

class API(Controller):
    
    def add_node(self):
        post = self.request.env['wsgi.input'].read(300000000)
        try:
            node = json.loads(post)
            self.logger.info(node)
        except Exception as e:
            self.logger.exception(e)
            return Reponse(json.dumps(dict(response=e), cls=ComplexEncoder))

        location = models.Location(id=node.get('location_id'))
        node_obj = models.Node()

        for sensor in node.get('sensors'):
            s = models.NodeSensor()
            fill_object(s, sensor, nots=['type'])
            s.type = models.Sensor.find_one({'type':sensor['type']})
            node_obj.sensors.append(s)

        for out in node.get('outputs'):
            s = models.Output()
            fill_object(s, out)
            node_obj.outputs.append(s)

        for inp in node.get('inputs'):
            s = models.Input()
            fill_object(s, inp)
            node_obj.inputs.append(s)

        for trig in node.get('triggers'):
            s = models.Trigger()
            fill_object(s, trig)
            node_obj.triggers.append(s)

        for rep in node.get('repeaters'):
            s = models.Repeater()
            fill_object(s, rep)
            node_obj.repeaters.append(s)

        for cl in node.get('clocks'):
            s = models.Clock()            
            fill_object(s, cl, nots=['time'])
            s.time = models.Time()
            s.time.hour = cl.get('time')[0]
            s.time.minute = cl.get('time')[1]
            node_obj.clocks.append(s)

        for pid in node.get('pids'):
            s = models.PID()            
            fill_object(s, pid)
            node_obj.pids.append(s)

        id = str(ObjectId())
        node_obj.name = node.get('name')
        node_obj.id = id
        node_obj.webcam = node.get('webcam')
        location.nodes.append(node_obj)
        location.save()
        return Response(json.dumps(dict(id=node_obj.id), cls=ComplexEncoder))

    def register_location(self):
        self.logger.info("got location")
        loc = models.Location()
        loc.location = [1,1]
        loc.save()
        return Response(json.dumps(dict(id=loc._id), cls=ComplexEncoder))

    def sensor_values(self):
        post = self.request.env['wsgi.input'].read(300000000)
        try:
            payload = json.loads(post)
            conn = models.SensorValue._connection()
            self.logger.info(payload)
        except Exception as e:
            self.logger.exception(e)
            return Reponse(json.dumps(dict(response=e), cls=ComplexEncoder))

        ts = datetime.datetime.fromtimestamp(payload.get('timestamp')/1000)
        loc_id = payload.pop('location_id')
        for node in payload.get('nodes'):
            node_id = node.pop('id')
            for k, sensor in node.iteritems():
                val = dict(
                    timestamp=ts,
                    location=ObjectId(loc_id),
                    node=node_id,
                    sensor=sensor.get('id'),
                    value=sensor.get('value'),
                )        
                conn.insert(val)                               
        return Response(json.dumps(dict(success=True)))