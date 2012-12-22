from envy.controller import Controller
from envy.response import Response
import models.node as node
from util.jsontools import ComplexEncoder
import json
import settings

class DefaultController(Controller):

    def default_response(self, template, **kwargs):
        home = self.request.env.get('HTTP_HOST')
        loc = self.session.location.json() if hasattr(self.session, 'location') else {}
        sensors = {str(value._id): value.json() for value in node.Sensor.find()}
        return Response(self.render(template, values=json.dumps(loc, cls=ComplexEncoder), 
        	url=home, settings=settings, session=self.session, 
        	sensors=json.dumps(sensors, cls=ComplexEncoder), **kwargs))