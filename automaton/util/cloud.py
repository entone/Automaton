import urllib2
import json
import settings
import util
from util import aes
from util.jsontools import ComplexEncoder

class Cloud(object):

    def __init__(self):
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))

    def __getattr__(self, method):
        def call(payload=None):
            url = settings.CLOUD_API+method
            data = ""
            if payload: data = json.dumps(payload, cls=ComplexEncoder)
            enc = aes.encrypt(data, settings.KEY)
            req = urllib2.Request(url, enc)
            res = urllib2.urlopen(req)
            st = res.read()
            st = aes.decrypt(st, settings.KEY)
            res.close()
            st = json.loads(st)
            return st

        return call



