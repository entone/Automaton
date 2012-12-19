import util
import humongolus as orm
from models.node import Location

class PasswordValidator(orm.FieldValidator):

	def validate(self, val, doc=None):
		return util.encrypt_password(val)

class User(orm.Document):
	firstname = field.Char()
	lastname = field.Char()
	email = field.Email(unique=True)
	password = field.Char(validate=PasswordValidator)
	locations = orm.List(type=Location)
