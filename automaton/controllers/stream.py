import gevent
import random
import datetime
import simplejson as json
import sqlite3
import settings
import util
from envy.controller import Controller
from envy.response import Response
from util.jsontools import ComplexEncoder
from util.subscriber import Subscriber
from util.rpc import RPC
from util import aes

logger = util.get_logger(__name__)

class Graph(Controller):

    def display(self):
        res = {}
        self.rpc = RPC(port=settings.CLIENT_RPC)
        res = self.rpc.send(dict(method='get_nodes'), settings.KEY)
        home = self.request.env.get('HTTP_HOST')
        db = sqlite3.connect("automaton.db", detect_types=sqlite3.PARSE_DECLTYPES)
        cur = db.cursor()
        q_t = datetime.datetime.utcnow()-datetime.timedelta(hours=settings.HISTORICAL_DISPLAY)
        for n in res:
            n['historical'] = cur.execute('SELECT * FROM logs WHERE node=? AND timestamp > ? LIMIT 20', (n.get('name'),q_t)).fetchall()
        
        self.logger.debug("Got Nodes: %s" % res)
        self.rpc.done()
        db.close()
        return Response(self.render("graphs/humidity.html", values=json.dumps(res, cls=ComplexEncoder), url=home))

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
        rpc.done()
        return Response(json.dumps(res, cls=ComplexEncoder))

