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
    index = field.Integer()
    display = field.Char()
    id = field.Char()
    change = field.Integer()
    data_rate = field.Integer()
    type = field.ModelChoice(type=Sensor)
    value = field.Float()

class Input(orm.EmbeddedDocument):
    index = field.Integer()
    display = field.Char()
    type = field.Char()

class Output(orm.EmbeddedDocument):
    index = field.Integer()
    display = field.Char()
    type = field.Char()

class Time(orm.EmbeddedDocument):
    hour = field.Integer()
    minute = field.Integer()

class Clock(orm.EmbeddedDocument):
    time = Time()
    output = field.Char()
    state_change = field.Boolean()

class Repeater(orm.EmbeddedDocument):
    run_for = field.Integer()
    every = field.Integer()
    output = field.Char()
    padding = field.Integer()
    state_change = field.Boolean()

class Trigger(orm.EmbeddedDocument):
    input = field.Char()
    min = field.Float()
    max = field.Float()
    output = field.Char()

class PID(orm.EmbeddedDocument):
    input = field.Char()
    output = field.Char()
    set_point = field.Float()
    update = field.Integer()
    check = field.Integer()
    proportional = field.Float()
    integral = field.Float()
    derivative = field.Float()


class Node(orm.EmbeddedDocument):
    id = field.Char()
    name = field.Char(required=True)
    webcam = field.Char()
    sensors = orm.List(type=NodeSensor)
    outputs = orm.List(type=Output)
    inputs = orm.List(type=Input)
    triggers = orm.List(type=Trigger)
    repeaters = orm.List(type=Repeater)
    clocks = orm.List(type=Clock)
    pids = orm.List(type=PID)

class Location(orm.Document):
    _db = 'automaton'
    _collection = 'locations'
    name = field.Char()
    nodes = orm.List(type=Node)
    location = field.Geo()

    def get_node(self, id):
        for n in self.nodes:
            if n.id == id: return n

        return None

class SensorValue(orm.Document):
    _db = 'automaton'
    _collection = 'sensor_values'
    _indexes = [
        orm.Index('node', key=[("node", orm.Index.DESCENDING)], unique=False),
        orm.Index('location', key=[("location", orm.Index.DESCENDING)], unique=False),
        orm.Index('timestamp', key=[("timestamp", orm.Index.DESCENDING)], unique=False),
        orm.Index('sensor', key=[("sensor", orm.Index.DESCENDING)], unique=False),
    ]
    timestamp = field.Date()
    location = field.DocumentId(type=Location)
    node = field.Char()
    sensor = field.Char()
    value = field.Float()