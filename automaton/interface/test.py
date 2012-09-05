import random
import gevent
from util.publisher import Publisher
from trigger import Trigger

temp = Trigger('temp', 'lettuce', 30, float('inf'), 'fan', True, False, "tcp://localhost:5555")

class Test(Publisher):

    def __init__(self, *args, **kwargs):
        self.ouputs = dict(
            plant_light = dict(
                index=0,
            ),
            fan = dict(
                index=1,
            ),
            pump=dict(
                index=2,
            )
        )
        super(Test, self).__init__(*args, **kwargs)

    def run(self):
        while True:
            self.publish(
                dict(
                    node='lettuce',
                    type='temp',
                    value=random.randint(0, 50)
                )
            )

            self.publish(
                dict(
                    node='lettuce',
                    type='humidity',
                    value=random.randint(0, 100)
                )
            )

            self.publish(
                dict(
                    node='lettuce',
                    type='ph',
                    value=random.randint(0, 14)
                )
            )

            gevent.sleep(1)




