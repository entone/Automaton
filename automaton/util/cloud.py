import urllib
import json
import logging
from automaton import settings
from automaton.util import aes
from automaton.util.jsontools import ComplexEncoder

class Cloud(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def __getattr__(self, method):
        def call(payload=None):
            url = settings.CLOUD_API+method
            self.logger.debug(url)
            data = ""
            if payload: data = json.dumps(payload, cls=ComplexEncoder)
            enc = aes.encrypt(data, settings.KEY)
            res = urllib.urlopen(url, enc)
            st = res.read()
            st = aes.decrypt(st, settings.KEY)
            res.close()
            st = json.loads(st)
            return st

        return call



