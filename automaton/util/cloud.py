import urllib2
import json
import settings
import util
from util.jsontools import ComplexEncoder

class Cloud(object):

    def __init__(self):
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))

    def __getattr__(self, method):
        def call(payload=None):
            url = settings.CLOUD_URI+method
            data = ""
            if payload: data = json.dumps(payload, cls=ComplexEncoder)
            req = urllib2.Request(url, data)
            res = urllib2.urlopen(req)
            st = res.read()
            res.close()
            st = json.loads(st)
            return res

        return call



