import datetime
import simplejson as json
import settings
import util
import models.node as node
from controllers import DefaultController
from envy.response import Response
from util.jsontools import ComplexEncoder
from util.decorators import level

class NodeSettings(DefaultController):

    @level(0)
    def index(self):
        return self.default_response("settings.html")

    @level(0)
    def save(self):
        settings = util.get_request_payload(self.request)
        node_id = settings.pop("node")
        loc = node.Location.find_one({
            "nodes.id":node_id,
        })
        n_obj = loc.get_node(node_id)
        self.update_settings(n_obj, settings)
        loc.save()
        self.logger.debug(n_obj._json())
        return Response(json.dumps(settings))

    def update_settings(self, obj, settings):
        for k,v in settings.iteritems():           
            typ = k.split("__")[0]
            if typ.startswith("clock"):
                for c in obj.clocks:
                    if c.id == typ and c.state_change == True:
                        c.time.hour = v[0]/60
                        c.time.minute = v[0]%60
                    elif c.id == typ and c.state_change == False:
                        c.time.hour = v[1]/60
                        c.time.minute = v[1]%60
            elif typ.startswith("repeater"):
                for r in obj.repeaters:
                    if r.id == typ:
                        r.run_for = v.get("run_for__%s"%typ)
                        r.every = v.get("every__%s"%typ)
            elif typ.startswith("trigger"):                
                for t in obj.triggers:
                    self.logger.info(t._json())
                    self.logger.info(v)
                    if t.id == typ:
                        ty = typ[8:].replace("-", "_")
                        t.min = v.get("min__%s"%ty)
                        max = v.get("max__%s"%ty) if v.get("max__%s"%ty) else float("inf")
                        t.max = max

            elif typ.startswith("pid"):                
                for p in obj.pids:
                    if p.id == typ:
                        p.set_point = v.get("set_point__%s"%typ)

        return True
