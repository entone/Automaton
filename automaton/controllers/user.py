import gevent
import random
import datetime
import simplejson as json
import settings
import util
import models.node as node_models
import models.user as user_models
from controllers import DefaultController
from envy.response import Response
from util.jsontools import ComplexEncoder
from util import aes
from bson.objectid import ObjectId

class User(DefaultController):

    def signin(self):
        return self.default_response('signin.html')

    def signup(self):
        print self.session
        return self.default_response('signup.html')

    def signout(self):
        resp = Response("bye", status="301 Moved Permanently", headers=[('Location', '/signin'),])
        self.session.logout = True
        return resp

    def auth(self):
        payload = util.get_request_payload(self.request)
        user = user_models.User.find_one({'email':payload.get('email')})
        if not user == None:
            if user.check_password(payload.get('password')):
                self.session.user = user
                return Response(json.dumps(dict(success=True)))

        return Response(json.dumps(dict(error=True)))

    def create_account(self):
        payload = util.get_request_payload(self.request)
        user = user_models.User()
        user.admin = False
        user.level = 1
        user.firstname = payload.pop('firstname')
        user.lastname = payload.pop('lastname')
        user.email = payload.pop('email')
        user.password = payload.pop('password')
        node = payload.pop('node')
        q = {'nodes.id':node}
        self.logger.info(q)
        location = node_models.Location.find_one(q)
        self.logger.info(location)
        if not location == None:
            loc = user_models.UserLocation()
            loc.location = location
            user.locations.append(loc)
        else:
            return Response(json.dumps(dict(error="Invalid Unit ID")))
        try:
            user.save()
            self.session.user = user
            return Response(json.dumps(dict(success=True)))
        except Exception as e:
            return Response(json.dumps(dict(error=e)))
