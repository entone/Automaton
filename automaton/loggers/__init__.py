import sqlite3
import gevent
import datetime

class Logger(object):

    def __init__(self, node):
        self.node = node
        self.db = sqlite3.connect("automaton.db", detect_types=sqlite3.PARSE_DECLTYPES)
        try:
            self.db.execute('''CREATE TABLE logs (timestamp timestamp, node text, sensor text, value real, type text)''')
        except Exception as e:
            print e
        gevent.spawn(self.log)
    
    def log(self):
        while True:
            print "Logging"
            for i in self.node.sensors:
                ob = i.json()
                ob['timestamp'] = datetime.datetime.utcnow();
                self.db.execute("INSERT INTO logs VALUES(?,?,?,?,?)", (ob.get('timestamp'), ob.get('node'), ob.get('display'), ob.get('value'), ob.get('id')))
                self.db.commit()

            gevent.sleep(10*60)