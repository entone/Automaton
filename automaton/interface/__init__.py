import gevent
import random
from util.publisher import Publisher

class Interface(Publisher):

    def run(self):
        while True:
            humidity = dict(value=random.randint(1, 100), node='lettuce', type='humidity')
            ph = dict(value=random.randint(0,14), node='lettuce', type='ph')
            self.publish(humidity)
            self.publish(ph)
            gevent.sleep(.5)

