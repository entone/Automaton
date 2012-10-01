import sqlite3
import gevent
import datetime
import settings

class Logger(object):

    def __init__(self, manager):
        self.manager = manager
        self.db = sqlite3.connect("automaton.db", detect_types=sqlite3.PARSE_DECLTYPES)
        try:
            self.db.execute('''CREATE TABLE logs (timestamp timestamp, node text, sensor text, value real, type text)''')
        except Exception as e:
            print e
        gevent.spawn(self.log)
    
    def log(self):
        while True:
            print "Logging"
            nodes = self.manager.get_sensor_values()
            for k, v in nodes.iteritems():
                for i, s in v.iteritems():
                    ob = s
                    ob['timestamp'] = datetime.datetime.utcnow();
                    self.db.execute("INSERT INTO logs VALUES(?,?,?,?,?)", (ob.get('timestamp'), ob.get('node'), ob.get('display'), ob.get('value'), ob.get('id')))
                    self.db.commit()

            gevent.sleep(settings.LOG_INTERVAL)