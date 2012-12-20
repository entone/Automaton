import gevent
import random
import datetime
import simplejson as json
import settings
import util
import csv
import cStringIO
import models.node as node
from envy.controller import Controller
from envy.response import Response
from util.jsontools import ComplexEncoder
from util.subscriber import Subscriber
from util.rpc import RPC

loc_id = "50ccfc511f99cd16ea70c3ea"

class Historical(Controller):

    def index(self):
        location = node.Location(id=loc_id)
        self.logger.debug("Got location: %s" % location)
        home = self.request.env.get('HTTP_HOST')
        return Response(self.render("historical.html", values=json.dumps(location.nodes, cls=ComplexEncoder), location=location, url=home, settings=settings, session=self.session))

    def get_data(self, node_id, type, frm=None, to=None):
        time = datetime.datetime.utcnow()
        if type == 'hour':
            time = datetime.datetime.utcnow()-datetime.timedelta(hours=1)
        if type == 'day':
            time = datetime.datetime.utcnow()-datetime.timedelta(hours=24)
        if type == 'week':
            time = datetime.datetime.utcnow()-datetime.timedelta(days=7)
        if type == 'month':
            time = datetime.datetime.utcnow()-datetime.timedelta(days=30)        
        q = dict(
            node=node_id, 
            timestamp={'$gte':time}
        )
        if type == 'custom':
            frm = datetime.datetime.strptime(frm, "%m-%d-%Y")
            to = datetime.datetime.strptime(to, "%m-%d-%Y")
            q['timestamp'] = {'$gte':frm, '$lt':to}

        self.logger.debug("Query: %s" % q)
        res = node.SensorValue.find(q, as_dict=True, fields={'timestamp':1,'sensor':1,'value':1})
        return res        

    def csv(self, node_id, type, frm=None, to=None):
        location = node.Location(id=loc_id)
        node_obj = location.get_node(node_id)
        res = self.get_data(node_id, type, frm, to)
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
        location = node.Location(id=loc_id)
        node_obj = location.get_node(node_id)
        res = self.get_data(node_id, type, frm, to)
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

        for r in res:
            d = get_obj(r.get('sensor'))
            d['data'].append([r.get('timestamp'), r.get('value')])

        res = dict(name=node_obj.name, data=ret)
        return Response(json.dumps(dict(result=res), cls=ComplexEncoder))

