from pymongo.connection import Connection
import logging
import humongolus as orm
import humongolus.field as field

class Sensor(orm.Document):
	_db = 'automaton'	
	_collection = 'sensors'
	_indexes = [
		orm.Index('type', key=[("type", orm.Index.DESCENDING)], unique=True)
	]
	type = field.Char(required=True)
	decorator = field.Char()

class NodeSensor(orm.EmbeddedDocument):
	type = field.ModelChoice(type=Sensor)
	current_value = field.Float()

class Node(orm.EmbeddedDocument):
	name = field.Char(required=True)
	sensors = orm.List(type=NodeSensor)
	webcam = field.Char()

class Location(orm.Document):
	_db = 'automaton'
	_collection = 'locations'
	nodes = orm.List(type=Node)
	location = field.Geo()