import gevent
import random
import datetime
import json
import zmq.green as zmq
from envy.controller import Controller
from envy.response import Response
from util.jsontools import ComplexEncoder
from util.subscriber import Subscriber

class Graph(Controller):

    def display(self):
        self.rpc = zmq.Context()
        self.rpc_socket = self.rpc.socket(zmq.REQ)
        self.rpc_socket.setsockopt(zmq.LINGER, 10)
        self.rpc_socket.connect("tcp://127.0.0.1:6666")
        self.rpc_socket.send(json.dumps(dict(method='get_values')))
        home = self.request.env.get('HTTP_HOST')
        res = {}
        try:
            res = self.rpc_socket.recv(zmq.NOBLOCK)
            res = json.loads(res)
            print res
        except Exception as e:
            self.logger.exception(e)
        return Response(self.render("graphs/humidity.html", values=res, url=home))

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
            print ws
            print "IN"
            def write_out(ob):
                st = "%s\n" % json.dumps(ob, cls=ComplexEncoder)
                print "web socket: %s" % st
                ws.send(st)
            sub = Subscriber("tcp://localhost:5555", callback=write_out, spawn=False)
        except Exception as e:
            self.logger.exception(e)
            