import gevent
import random
import datetime
from envy.controller import Controller
from envy.response import Response
from util.jsontools import ComplexEncoder
from util.subscriber import Subscriber
import json
import zmq.green as zmq

class Graph(Controller):

    def display(self):
        self.rpc = zmq.Context()
        self.rpc_socket = self.rpc.socket(zmq.REQ)
        self.rpc_socket.connect("tcp://127.0.0.1:6666")
        self.rpc_socket.send(json.dumps(dict(method='get_values')))
        res = self.rpc_socket.recv()
        res = json.loads(res)
        print res
        return Response(self.render("graphs/humidity.html", values=res))

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
            