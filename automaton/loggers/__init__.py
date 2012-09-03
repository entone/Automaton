from pymongo.connection import Connection
from util.subscriber import Subscriber

class Logger(object):

    def __init__(self):
        try:
            self.conn = Connection()
            self.conn['test'].drop_collection("realtime_log")
            self.conn['test'].create_collection("realtime_log", size=209715200, capped=True)    
            self.conn['test']['realtime_log'].ensure_index([('type',1), ('node',1)])
            self.subscriber = Subscriber("tcp://localhost:5555", self.log)
        except Exception as e:
            print e
    
    def log(self, ob):
        self.conn['test']['realtime_log'].insert(ob)