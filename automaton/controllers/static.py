import os
from envy.controller import Controller
from envy.response import Response

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '../templates/')

class Static(Controller):

    def index(self, file):
        path = os.path.join(TEMPLATE_DIR, file)
        print "PATH: %s" % path
        f = open(path).read()
        return Response(f)
