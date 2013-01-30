import datetime
import simplejson as json
import settings
import util
import models.node as node
from controllers import DefaultController
from envy.response import Response
from util.jsontools import ComplexEncoder
from util.decorators import level

class ManualReadings(DefaultController):

    @level(0)
    def index(self):
        return self.default_response("manual_readings.html")

    @level(0)
    def save(self):
        marker = util.get_request_payload(self.request)
        typ = marker.get('sensor')
        conn = node.SensorValue._connection()
        if typ == 'marker':
            cls = node.Marker
        else:
            cls = node.SensorValue

        d = node.Location.find_one({
            "nodes.id":marker.get('node'),
        })
        
        o = dict(
            node=marker.get('node'),
            location=d.get('_id'),
            timestamp=datetime.datetime.utcnow(),
            sensor=typ,
            value=marker.get('value'),
        )
        id = conn.insert(o)
        return Response(json.dumps(dict(id=str(id))))
