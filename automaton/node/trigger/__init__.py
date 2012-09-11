from util.subscriber import Subscriber
from util.rpc import RPC
import gevent
import datetime
import settings

class Clock(object):
    time = None
    output = None
    state_change = None

    def __init__(self, time, output, state):
        self.time = time
        self.output = output
        self.state_change = state
        self.logger = settings.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        gevent.spawn(self.run)

    def run(self):
        while True:
            now = datetime.datetime.utcnow()
            self.logger.debug("Now: %s" % now)
            self.logger.debug(self.time)
            if now.hour == self.time[0] and now.minute == self.time[1]:
                self.output.set_state(self.state_change)

            gevent.sleep(60)

    def json(self):
        return dict(
            time=self.time,
            output=self.output.type,
            state_change=self.state_change,
        )

class Repeater(object):
    run_for = 0
    every = 0
    output = None
    state_change = True
    times = {}

    def __init__(self, output, run_for=0, every=60, state=True, padding=0):
        self.run_for = run_for
        self.every = every
        self.output = output
        self.state = state
        self.padding = padding
        self.logger = settings.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        self.times = {}
        for t in xrange(0, 1440, self.every):
            h_on = t/60 if t else 0
            m_on = t%60 if t else 0
            m_on=m_on+self.padding
            self.times["%i:%i" % ((h_on, m_on))] = self.state_change

            h_off = h_on
            m_off = m_on+self.run_for
            self.times["%i:%i" % ((h_off, m_off))] = not self.state_change

        self.logger.info("Repeater Set For: %s" % self.times)
        gevent.spawn(self.run)

    def run(self):
        while True:
            now = datetime.datetime.utcnow()
            self.logger.debug("Now: %s" % now)            
            time = "%i:%i" % (now.hour, now.minute)
            self.logger.debug(time)
            t = self.times.get(time)
            if not t == None: self.output.set_state(t)
            gevent.sleep(60)

    def json(self):
        return dict(
            run_for=self.run_for,
            every=self.every,
            output=self.output.type,
            padding=self.padding,
            state_change=self.state_change,
        )


class Trigger(Subscriber):
    
    input = None
    min = None
    max = None
    output = None
    state_change = None
    current_state = None

    def __init__(self, input, output, min, max, state, current_state, port):
        self.input = input
        self.min = min
        self.max = max
        self.output = output
        self.state = state
        self.current_state = current_state
        self.logger = settings.get_logger("%s.%s" % (self.__module__, self.__class__.__name__))
        super(Trigger, self).__init__(port=port, callback=self.handle_event)


    def handle_event(self, ob, **kwargs):
        state_change = self.test_change(ob)
        if not state_change == None:
            self.current_state = state_change
            self.output.set_state(state_change)

        return True

    def test_change(self, ob):
        if not self.input.type == ob.get('type'): return None
        if not self.input.interface.name == ob.get('node'): return None

        val = ob.get('value')
        if (val < self.min or val > self.max) and (self.current_state == self.state):
            return not self.state
        elif self.min <= ob.get('value') < self.max and not self.current_state == self.state:
            return self.state

        return None

    def json(self):
        return dict(
            input=self.input.type,
            min=self.min,
            max=self.max,
            output=self.output.type,
            state_change=self.state_change,
        )