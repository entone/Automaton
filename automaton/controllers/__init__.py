from envy.controller import Controller
from envy.response import Response
import models.node as node
from util.jsontools import ComplexEncoder
import json
import settings

loc_id = "50ccfc511f99cd16ea70c3ea"

class DefaultController(Controller):

    def default_response(self, template, **kwargs):
        location = node.Location(id=loc_id)
        self.logger.debug("Got location: %s" % location)
        home = self.request.env.get('HTTP_HOST')
        return Response(self.render(template, values=json.dumps(location.nodes, cls=ComplexEncoder), location=location, url=home, settings=settings, session=self.session, **kwargs))