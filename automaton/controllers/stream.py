import gevent
import random
import datetime
import simplejson as json
import sqlite3
from envy.controller import Controller
from envy.response import Response
from util.jsontools import ComplexEncoder
from util.subscriber import Subscriber
from util.rpc import RPC

class Graph(Controller):

    def display(self):
        res = {}
        self.rpc = RPC(port=5553)
        res = self.rpc.send(dict(method='get_nodes'))
        home = self.request.env.get('HTTP_HOST')
        db = sqlite3.connect("automaton.db", detect_types=sqlite3.PARSE_DECLTYPES)
        cur = db.cursor()
        q_t = datetime.datetime.utcnow()-datetime.timedelta(hours=1)
        for n in res:
            n['historical'] = cur.execute('SELECT * FROM logs WHERE node=? AND timestamp > ? LIMIT 20', (n.get('name'),q_t)).fetchall()
        
        print "Got nodes: %s" % res
        return Response(self.render("graphs/humidity.html", values=json.dumps(res, cls=ComplexEncoder), url=home))

    def historical(self, name):
        db = sqlite3.connect("automaton.db", detect_types=sqlite3.PARSE_DECLTYPES)
        cur = db.cursor()
        q_t = datetime.datetime.utcnow()-datetime.timedelta(hours=1)
        res = cur.execute('SELECT * FROM logs WHERE node=? AND timestamp > ?', (name,q_t)).fetchall()
        print res
        return Response(json.dumps(res, cls=ComplexEncoder))

    def index(self):
        try:
            ws = self.request.env['wsgi.websocket']
            def write_out(ob):
                st = "%s\n" % json.dumps(ob, cls=ComplexEncoder)
                print "Message: %s" % st
                ws.send(st)
            sub = Subscriber(port=5554, callback=write_out, spawn=False)
        except Exception as e:
            self.logger.exception(e)
    

    def control(self):
        self.rpc = RPC(port=5553)
        ws = self.request.env['wsgi.websocket']
        while True:
            try:
                mes = ws.receive()
                mes = json.loads(mes)
                mes['method'] = 'set_output_state'
                res = self.rpc.send(mes)
                ws.send("%s\n" % json.dumps(res))
            except Exception as e: pass
            gevent.sleep(.1)

