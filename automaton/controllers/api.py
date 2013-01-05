import gevent
import random
import datetime
import simplejson as json
import settings
import util
import models.node as node_models
from envy.controller import Controller
from envy.response import Response
from util.jsontools import ComplexEncoder
from util import aes
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
        node = util.get_request_payload(self.request, encrypted=True)
        location = node_models.Location(id=node.get('location_id'))
        node_obj = node_models.Node()

        for sensor in node.get('sensors'):
            s = node_models.NodeSensor()
            fill_object(s, sensor, nots=['type'])
            s.type = node_models.Sensor.find_one({'type':sensor['type']})
            node_obj.sensors.append(s)

        for out in node.get('outputs'):
            s = node_models.Output()
            fill_object(s, out)
            node_obj.outputs.append(s)

        for inp in node.get('inputs'):
            s = node_models.Input()
            fill_object(s, inp)
            node_obj.inputs.append(s)

        for trig in node.get('triggers'):
            s = node_models.Trigger()
            fill_object(s, trig)
            node_obj.triggers.append(s)

        for rep in node.get('repeaters'):
            s = node_models.Repeater()
            fill_object(s, rep)
            node_obj.repeaters.append(s)

        for cl in node.get('clocks'):
            s = node_models.Clock()            
            fill_object(s, cl, nots=['time'])
            s.time = node_models.Time()
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
        return Response(
            aes.encrypt(json.dumps(dict(id=node_obj.id), cls=ComplexEncoder), settings.KEY)
        )

    def register_location(self):
        self.logger.info("got location")
        loc = node_models.Location()
        loc.location = [1,1]
        loc.save()
        return Response(
            aes.encrypt(
                json.dumps(
                    dict(id=loc._id), 
                    cls=ComplexEncoder
                ), 
                settings.KEY
            )
        )

    def sensor_values(self):
        payload = util.get_request_payload(self.request, encrypted=True)
        conn = node_models.SensorValue._connection()
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
        return Response(
            aes.encrypt(
                json.dumps(
                    dict(success=True)
                ), 
                settings.KEY
            )
        )

    def save_image(self):
        payload = util.get_request_payload(self.request, encrypted=True)
        image = node_models.Image()
        image.timestamp = datetime.datetime.fromtimestamp(payload.get('timestamp')/1000)
        image.location = payload.get('location')
        image.node = payload.get('node')
        image.filename = payload.get('filename')
        image.save()
        return Response(
            aes.encrypt(
                json.dumps(
                    dict(success=True)
                ), 
                settings.KEY
            )
        )

