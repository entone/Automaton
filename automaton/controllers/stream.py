import gevent
import random
import datetime
import json
from envy.controller import Controller
from envy.response import Response
from util.jsontools import ComplexEncoder
from util.subscriber import Subscriber
from util.rpc import RPC

class Graph(Controller):

    def display(self):
        self.rpc = RPC("tcp://127.0.0.1:6666")
        res = self.rpc.send(dict(method='get_values'))
        home = self.request.env.get('HTTP_HOST')
        return Response(self.render("graphs/humidity.html", values=res, url=home))

    def index(self):
        try:
            ws = self.request.env['wsgi.websocket']
            def write_out(ob):
                st = "%s\n" % json.dumps(ob, cls=ComplexEncoder)
                ws.send(st)
            sub = Subscriber("tcp://localhost:5555", callback=write_out, spawn=False)
        except Exception as e:
            self.logger.exception(e)
    

    def control(self):
        self.rpc = RPC("tcp://127.0.0.1:6666")
        ws = self.request.env['wsgi.websocket']
        while True:
            mes = ws.receive()
            mes = json.loads(mes)
            print mes
            mes['method'] = 'toggle_output'
            res = self.rpc.send(mes)
            ws.send("%s\n" % json.dumps(res))
            gevent.sleep(.1)

