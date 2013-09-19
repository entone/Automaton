import sqlite3
import gevent
import datetime
from automaton import settings
from automaton import util
from automaton.util import aes
from automaton.util.cloud import Cloud

class Logger(object):

    def __init__(self, manager):
        self.manager = manager
        self.db = sqlite3.connect("automaton.db", detect_types=sqlite3.PARSE_DECLTYPES)
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        try:
            self.db.execute('''CREATE TABLE logs (timestamp timestamp, node text, sensor text, value real, type text)''')
        except Exception as e:
            print e
        gevent.spawn(self.log)
    
    def log(self):
        while True:
            gevent.sleep(settings.LOG_INTERVAL)
            self.logger.info("Logging")
            nodes = self.manager.get_sensor_values()
            for k, v in nodes['nodes'].iteritems():
                for i, s in v.iteritems():
                    ob = s
                    ob['timestamp'] = datetime.datetime.utcnow();
                    self.db.execute("INSERT INTO logs VALUES(?,?,?,?,?)", (ob.get('timestamp'), ob.get('node'), ob.get('display'), ob.get('value'), ob.get('id')))
                    self.db.commit()
            

class CloudLogger(object):

    def __init__(self, manager):
        self.manager = manager
        self.cloud = Cloud()
        self.logger = util.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.errors = 0
        gevent.spawn(self.log)
    
    def log(self):
        while True:
            gevent.sleep(settings.CLOUD_LOG_INTERVAL)
            self.logger.info("Logging")
            nodes = self.manager.get_sensor_values()
            nodes['timestamp'] = datetime.datetime.utcnow()
            self.logger.info(nodes)
            try:
                res = self.cloud.sensor_values(nodes)
                self.logger.info(res)
            except Exception as e:
                self.logger.exception(e)
