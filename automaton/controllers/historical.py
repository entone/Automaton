import gevent
import os
import random
import datetime
import simplejson as json
import settings
import util
import csv
import cStringIO
import models.node as node
from envy.controller import Controller
from controllers import DefaultController
from envy.response import Response
from util.jsontools import ComplexEncoder
from util.subscriber import Subscriber
from util.rpc import RPC
from util.decorators import level

def mod_date(f):
    t = os.path.getmtime(f)
    return datetime.datetime.fromtimestamp(t)

class Historical(DefaultController):

    @level(0)
    def index(self):
        return self.default_response("historical.html")

    def get_images(self, time=None, frm=None, to=None):
        da_files = []
        for root, dirs, files in os.walk(settings.TIMELAPSE_PATH):
            for name in files:
                if name.startswith('.') == False:
                    f = os.path.join(root, name)
                    size = os.path.getsize(f)
                    if size > 1000:
                        mod = mod_date(f)
                        filename = "%s%s" % ("/static/timelapse/", name)
                        obj = dict(mod=mod, file=filename)
                        if (frm and to) and mod >= frm and mod < to: 
                            da_files.append(obj)
                        elif time and mod >= time:
                            da_files.append(obj)

        da_files.sort()
        return da_files

    def get_data(self, node_id, type, frm=None, to=None):
        time = datetime.datetime.utcnow()
        step = 1
        if type == 'hour':            
            time = datetime.datetime.utcnow()-datetime.timedelta(hours=1)
        if type == 'day':
            step = 6
            time = datetime.datetime.utcnow()-datetime.timedelta(hours=24)
        if type == 'week':
            step = 18
            time = datetime.datetime.utcnow()-datetime.timedelta(days=7)
        if type == 'month':
            step = 36
            time = datetime.datetime.utcnow()-datetime.timedelta(days=30)        
        q = dict(
            node=node_id, 
            timestamp={'$gte':time}
        )
        if type == 'custom':
            step = 18
            frm = datetime.datetime.strptime(frm, "%m-%d-%Y")
            to = datetime.datetime.strptime(to, "%m-%d-%Y")
            q['timestamp'] = {'$gte':frm, '$lt':to}


        images = node.Image.find(q, as_dict=True, fields={'timestamp':1, 'filename':1}).sort('timestamp', 1)
        ret_images = []
        for img in images:
            ob = dict(
                file="%s%s" %("/static/timelapse/", img.get('filename')),
                mod=img.get('timestamp'),
            )
            ret_images.append(ob)
        res = node.SensorValue.find(q, as_dict=True, fields={'timestamp':1,'sensor':1,'value':1})
        res.batch_size(10000)
        res = [res[i] for i in xrange(0, res.count(), step)]
        return res, ret_images

    def csv(self, node_id, type, frm=None, to=None):
        node_obj = self.session.location.get_node(node_id)
        res, images = self.get_data(node_id, type, frm, to)
        ret = []
        csv_buffer = cStringIO.StringIO()
        csv_writer = csv.DictWriter(csv_buffer, ('node', 'sensor', 'timestamp', 'value'))
        csv_writer.writeheader()
        for i in res:
            row = dict(node=node_obj.name, sensor=i.get('sensor'), timestamp=i.get('timestamp'), value=i.get('value'))
            csv_writer.writerow(row)

        resp = Response(body=csv_buffer.getvalue(), headers=[('Content-Type', 'application/csv'), ('Content-Disposition', 'attachment; filename="%s-%s.csv"' % (node_obj.name, type))])
        return resp



    def data(self, node_id, type, frm=None, to=None):
        node_obj = self.session.location.get_node(node_id)
        res, images = self.get_data(node_id, type, frm, to)
        ret = []
        def get_obj(sensor):
            name = sensor
            for s in node_obj.sensors:
                if s.id == sensor: 
                    name = s.display
            for i in ret:
                if i.get('label') == name: return i

            o = {'label':name, 'data':[]}
            ret.append(o)
            return o

        markers = []
        for r in res:
            if r.get('sensor') == 'marker':
                markers.append([r.get('timestamp'), r.get('value')])
                continue
            d = get_obj(r.get('sensor'))
            d['data'].append([r.get('timestamp'), r.get('value')])

        res = dict(name=node_obj.name, data=ret, images=images, markers=markers)
        return Response(json.dumps(dict(result=res), cls=ComplexEncoder))

