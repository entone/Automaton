import os
from envy.controller import Controller
from envy.response import Response
import settings
import util

logger = util.get_logger(__name__)

class Static(Controller):

    def index(self, file):
    	try:
        	path = os.path.join(settings.TEMPLATE_DIRS[0], file)
        	logger.info("Static File: %s" % path)
        	f = open(path).read()
        	return Response(f)
        except Exception as e:
        	logger.exception(e)
