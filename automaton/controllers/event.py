from envy.controller import Controller
from envy.response import Response
from gunicorn.http.body import Body
from bson.objectid import ObjectId
import models
import json
from libs import jsontools

class Event(Controller):

    def submit(self, type):
        func = EVENTS.get(type)
        model = MODELS.get(type)
        data = self.request.env.get('wsgi.input').read()
        data = json.loads(data)
        try:
            obj = model()
            obj.type = type
            for k,v in data.iteritems():
                setattr(obj, k,v)
            
            if self.session.parent: 
                obj.parent = models.Share(id=self.session.parent)

            obj.save()
            self.logger.debug(obj.json())
            res = func(obj, self.session)
            return Response(json.dumps(res, cls=jsontools.ComplexEncoder))
        except Exception as e:
            self.logger.exception(e)

    def test(self):
        return Response(self.render("test.html", url="http://event-dev.barackobama.com:8000"))

    def api(self):
        return Response(self.render("api.js", url="http://event-dev.barackobama.com:8000/event"))

    def redirect(self, share_id):
        share = models.Share.find({"_id":ObjectId(share_id)})
        headers = [('Location','http://event-dev.barackobama.com:8000/test')]
        cb = models.Clickback()
        cb.type = 'clickback'
        cb.parent = share[0]
        cb.save()
        self.session.parent = share_id
        return Response("woot", headers=headers, status='302 Found')

    def tree(self):
        shares = models.Share.find(dict(
                type='share',
                parent=None
            ), as_dict=True
        )
        res = dict(name="root", children=[build_tree(s) for s in shares])
        self.logger.debug(res)
        return Response(json.dumps(res, cls=jsontools.ComplexEncoder))

    def display(self):
        f = self.request.GET.get('js', 'network.js')
        if isinstance(f, list): f = f[0]
        return Response(self.render("tree.html", js=f))

    def static(self, file):
        f = open("/vagrant/event_visualization/templates/%s" % file).read()
        return Response(f)

def build_tree(obj):
    m = MODELS.get(obj.get('type'))
    obj = m(id=obj.get('_id'))
    children = models.Event.find({"parent._id":obj._id}, as_dict=True)
    res = dict(type=obj.type)
    res['children'] = [build_tree(s) for s in children]
    return res

def ph_value(val):
    print "PH: %s" % val

def humidity_value(val):
    print "Humidity: %s" % val

def handle_share(obj, session):
    session.parent = str(obj._id)
    return dict(
        url="http://event-dev.barackobama.com:8000/redirect/%s" % str(obj._id),
        id=str(obj._id),
    )

def handle_all(obj, session):
    return dict(
        success=True
    )

MODELS = dict(
    share=models.Share,
    clickback=models.Clickback,
    donate=models.Donate,
    signup=models.Signup,
    rsvp=models.Signup,
    progress=models.Progress,
    like=models.Like
)

EVENTS = dict(
    share=handle_share,
    clickback=handle_all,
    donate=handle_all,
    signup=handle_all,
    rsvp=handle_all,
    progress=handle_all,
    like=handle_all
)