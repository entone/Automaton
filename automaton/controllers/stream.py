import gevent
import random
import datetime
from envy.controller import Controller
from envy.response import Response
from util.jsontools import ComplexEncoder
from util.subscriber import Subscriber
import json

class Graph(Controller):

    def display(self):
        return Response(self.render("graphs/humidity.html"))

    def humidity(self):
        try:
            ws = self.request.env['wsgi.websocket']
            conn = Connection()
            for data in conn['test']['realtime_log'].find({'type':'humidity'}, tailable=True):
                ws.send("%s\n" % json.dumps(data, cls=ComplexEncoder))
                gevent.sleep(.1)
        except Exception as e:
            self.logger.exception(e)

    def ph(self):
        try:
            ws = self.request.env['wsgi.websocket']
            def write_out(ob):   
                st = "%s\n" % json.dumps(ob, cls=ComplexEncoder)
                print "web socket: %s" % st
                ws.send(st)
            sub = Subscriber("tcp://localhost:5555", callback=write_out, spawn=False)
        except Exception as e:
            self.logger.exception(e)
            