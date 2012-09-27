import gevent
import zmq.green as zmq
import simplejson as json
from util.jsontools import ComplexEncoder
from util.subscriber import Subscriber
import settings

class PubSub(object):

    def __init__(self, owner, pub_port, sub_port, sub_filter="", spawn=True):
        self.pc = zmq.Context()
        self.pub = self.pc.socket(zmq.PUB)
        self.pub.bind("tcp://0.0.0.0:%s" % pub_port)
        self.logger = settings.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.logger.info("Publishing on: %s" % pub_port)
        self.sub_filter = sub_filter
        self.owner = owner
        self.sub = Subscriber(self.callback, port=sub_port, filter=sub_filter, spawn=spawn)

    def callback(self, obj, **kwargs):
        self.logger.info("Calling: %s" % obj)        
        try:           
            res = getattr(self.owner, obj.get("method"))(obj, **kwargs)
            self.publish(res)
        except Exception as e:
            self.logger.exception(e)

    def publish(self, obj):        
        st = json.dumps(obj, cls=ComplexEncoder)        
        try:
            self.pub.send(st)
            self.logger.info("Publishing: %s" % st)
            self.logger.info(self.pub)
        except Exception as e:
            self.logger.exception(e)
