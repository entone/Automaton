import gevent
import zmq.green as zmq
from util.subscriber import Subscriber
from util.broadcast import Client
from util import aes
import settings
import util

class PubSub(object):

    def __init__(self, owner, pub_port, sub_port, sub_filter="", broadcast=True, spawn=True, parse_message=None):
        if broadcast:
            self.pub = Client(pub_port)
        else:
            self.pc = zmq.Context()
            self.pub = self.pc.socket(zmq.PUB)
            self.pub.bind("tcp://*:%s" % pub_port)
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.logger.info("Publishing on: %s" % pub_port)
        self.sub_filter = sub_filter
        self.owner = owner
        self.sub = Subscriber(self.callback, port=sub_port, filter=sub_filter, broadcast=broadcast, spawn=spawn, parse_message=parse_message)

    def callback(self, obj, **kwargs):
        try:           
            res = getattr(self.owner, obj.get("method"))(obj, **kwargs)
            return res
        except Exception as e:
            self.logger.exception(e)

        return True


    def publish(self, st):
        try:
            self.logger.info("Publishing: %s" % st)
            self.pub.send(st)
        except Exception as e:
            self.logger.exception(e)
