import humongolus as orm
import humongolus.field as field

class Event(orm.Document):

    _db = "ofa"
    _collection = "events"
    _indexes = [orm.Index(name='parent', key=[('parent', 1)]), orm.Index(name='type', key=[('type', 1)])]

    type = field.Char(required=True)
    user = field.Char()
    created = field.Date()
    parent = field.DynamicDocument()
    url = field.Char()

class Share(Event):
    _type = "share"
    channel = field.Char()
    topic = field.Char()
    recipient = field.Char()
    algorithm = field.Char()
    campaign =  field.Char()
    shared = field.Boolean()
    version = field.Char()

class Clickback(Event):
    _type = "clickback"
    referrer = field.Char()
    ip = field.Char()

class Donate(Event):
    _type = "donate"
    amount = field.Float()

class Signup(Event):
    _type = "signup"
    email = field.Email()
    zip = field.Char()

class RSVP(Event):
    _type = "rsvp"
    event = field.Char()

class Progress(Event):
    _type = "progress"
    marker = field.Char()

class Like(Event):
    _type = "like"
    channel = field.Char()





