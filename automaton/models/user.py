import util
import datetime
import humongolus as orm
import humongolus.field as field
from models.node import Location

class Password(field.Char):

    def clean(self, val, doc=None):
        val = super(Password, self).clean(val, doc)
        try:
            algo, salt, hash = val.split("$")
            if algo == "sha1": return val
        except Exception as e:
            self.logger.exception(e)   
        return util.encrypt_password(val)

class UserLocation(orm.EmbeddedDocument):
    location = field.DocumentId(type=Location)

class User(orm.Document):
    _db = "automaton"
    _collection = "users"
    _indexes = [
        orm.Index('email', key=('email', orm.Index.DESCENDING), unique=True)
    ]
    firstname = field.Char()
    lastname = field.Char()
    email = field.Email(unique=True)
    password = Password(required=True)
    locations = orm.List(type=UserLocation)
    level = field.Integer()
    admin = field.Boolean()

    def check_password(self, password):
        self.logger.info(password)
        self.logger.info(self.password)
        return util.check_password(password, self.password)

    def allowed(self, level):
        return self.level >= level

class Session(orm.Document):
    _db = "automaton"
    _collection = "sessions"
    _indexes = [
        orm.Index('last_activity', key=[("last_activity", orm.Index.DESCENDING)], ttl=3600)
    ]
    last_activity = field.Date()
    logout = field.Boolean(default=False)
    user = field.DocumentId(type=User, required=False)

    def __init__(self, key=None, request=None):
        id = key.value if key else None
        super(Session, self).__init__(id=id)
        if self.user:
            self.user_obj = self._get('user')()

    def save(self, response=None):
        self.last_activity = datetime.datetime.utcnow()
        if self.logout:
            self.logger.info("Logging Out")
            response.cookie('automaton_session', "")
            return True
        else:     
            res = super(Session, self).save()
            self.logger.info("Session ID: %s" % self._id)
            response.cookie('automaton_session', self._id)
            return res
