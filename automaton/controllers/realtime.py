from flask import current_app, request, Blueprint, render_template, Response
import gevent
from automaton import settings
import random
import datetime
import simplejson as json
import sqlite3
from automaton import util
import automaton.models.node as node_models
from automaton.util.jsontools import ComplexEncoder
from automaton.util.subscriber import Subscriber
from automaton.util.rpc import RPC
from automaton.util import aes
from automaton.util.decorators import level

node = Blueprint(
    'node',
    __name__,
    template_folder='../html/templates/'
)

@node.route('/', methods=['GET'])
def display():
    return render_template("stream.html");

@node.route('/stream/')
def stream():
    try:
        ws = request.environ['wsgi.websocket']
        current_app.logger.info(ws)
    except Exception as e:
        current_app.logger.exception(e)    
    while True:
        try:
            ws.send(json.dumps({"int":random.randint(1, 10000)}))
        except Exception as e:
            return Response()
        gevent.sleep(1)

class Location(object):
    nodes = []

    def __init__(self):
        self.nodes = []

    def json(self):
        return dict(
            nodes = [n.json() for n in self.nodes]
        )

class Node(object):

    def __init__(self, obj):        
        self.obj = obj
        for k,v in obj.iteritems(): setattr(self, k, v)

    def json(self):
        return self.obj

"""
class Realtime(DefaultController):

    @level(0)
    def display(self, id=None):
        location = Location()
        self.rpc = RPC(port=settings.CLIENT_RPC, address='127.0.0.1')
        res = self.rpc.send(dict(method='get_nodes'), settings.KEY)        
        if id:
            for node in res:
                self.logger.info("Node ID: %s" % node.get('id'))
                if node.get('id') == id:
                    node['webcam'] = "%s%s" % (node.get('webcam'), settings.WEBCAM_VIDEO)
                    n = Node(node)
                    location.nodes.append(n)
        else:
            location.nodes = res
        home = self.request.env.get('HTTP_HOST')
        self.logger.debug("Got Nodes: %s" % location)
        sensors = {str(value._id): value.json() for value in node_models.Sensor.find()}
        return Response(self.render("node.html", values=json.dumps(location.json(), cls=ComplexEncoder), 
            url=home, settings=settings, session=self.session, location=location,
            sensors=json.dumps(sensors, cls=ComplexEncoder)))

    def historical(self, name):
        db = sqlite3.connect("automaton.db", detect_types=sqlite3.PARSE_DECLTYPES)
        cur = db.cursor()
        q_t = datetime.datetime.utcnow()-datetime.timedelta(hours=settings.HISTORICAL_DISPLAY)
        res = cur.execute('SELECT * FROM logs WHERE node=? AND timestamp > ?', (name,q_t)).fetchall()
        self.logger.debug(res)
        return Response(json.dumps(res, cls=ComplexEncoder))

    def index(self):
        ws = self.request.env['wsgi.websocket']
        def write_out(ob):
            try:
                st = "%s\n" % json.dumps(ob, cls=ComplexEncoder)
                self.logger.debug("Message: %s" % st)
                ws.send(st)
                return True
            except Exception as e:
                self.logger.info("Connection Closed: %s" % ws)
                return False
        sub = Subscriber(callback=write_out, port=settings.CLIENT_SUB, broadcast=False, spawn=False, parse_message=self.parse_message)
        return Response('')
    
    def parse_message(self, message):
        return aes.decrypt(message, settings.KEY)

    def control(self):
        rpc = RPC(port=settings.CLIENT_RPC)
        mes = self.request.env.get('wsgi.input').read()
        mes = json.loads(mes)
        mes['method'] = 'set_output_state'
        res = rpc.send(mes, settings.KEY)
        return Response(json.dumps(res, cls=ComplexEncoder))

"""