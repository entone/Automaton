import gevent
import datetime
import logging
from automaton.util import pid
from automaton import settings
from automaton import util


class Clock(object):
    time = None
    output = None
    state_change = None

    def __init__(self, time, output, state):
        self.time = time
        self.output = output
        self.id = "clock_%s" % self.output.id
        self.state_change = state
        self.logger = logging.getLogger(__name__)
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
            id=self.id,
            time=self.time,
            output=self.output.display,
            state_change=self.state_change,
            cls=self.__class__.__name__
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
        self.id = "repeater_%s" % self.output.id
        self.logger = logging.getLogger(__name__)
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
            id=self.id,
            run_for=self.run_for,
            every=self.every,
            output=self.output.display,
            padding=self.padding,
            state_change=self.state_change,
            cls=self.__class__.__name__
        )




class Trigger(object):
    
    input = None
    min = None
    max = None
    output = None
    state_change = None
    current_state = None

    def __init__(self, input, output, min, max, state, current_state):
        self.input = input
        self.min = min
        self.max = max
        self.output = output
        self.id = "trigger_%s%s" % (self.input.id, self.output.id)
        self.state = state
        self.current_state = current_state
        self.logger = logging.getLogger(__name__)

    def handle_event(self, ob, **kwargs):
        state_change = self.test_change(ob)
        if not state_change == None:
            self.current_state = state_change
            self.output.set_state(state_change)

        return True

    def test_change(self, ob):
        if not self.input.type == ob.get('type'): return None
        if not self.input.interface.name == ob.get('node'): return None
        #check if this is an input or sensor
        val = ob.get('value')
        if isinstance(val, bool):
            if val == self.min and self.current_state == self.state:
                return not self.state
            elif val == self.min:
                return self.state

        if (val < self.min or val > self.max) and (self.current_state == self.state):
            return not self.state
        elif self.min <= ob.get('value') < self.max and not self.current_state == self.state:
            return self.state

        return None

    def json(self):
        return dict(
            id=self.id,
            input=self.input.type,
            min=self.min,
            max=self.max,
            output=self.output.type,
            current_state=self.current_state,
            cls=self.__class__.__name__
        )

class PID(object):
    input = None
    output = None
    state = True

    def __init__(self, input, output, state, set_point, update=60, check=30, P=2.0, I=0.0, D=1.0):
        self.input = input
        self.output = output
        self.id = "pid_%s%s" % (self.input.id, self.output.id)
        self.state = state
        self.set_point = set_point
        self.P = P
        self.I = I
        self.D = D
        self.pid = pid.PID(P,I,D)
        self.pid.setPoint(set_point)
        self.logger = logging.getLogger(__name__)
        self.update = update
        self.check = check
        gevent.spawn(self.run)

    def run(self):
        counter = 0
        time_check = self.check
        while True:
            try:
                val = self.input.get_value()                
                if val: error = self.pid.update(val)
                else: error = 0
                if counter == time_check:
                    counter = 0
                    self.current_state = self.state
                    self.output.set_state(self.state)
                    gevent.sleep(error)
                    v = not self.state
                    self.output.set_state(v)
                    continue
                counter+=1
            except Exception as e:
                self.logger.exception(e)
            gevent.sleep(self.update)


    def json(self):
        return dict(
            id=self.id,
            input=self.input.type,
            output=self.output.type,
            set_point=self.set_point,
            update=self.update,
            check=self.check,
            proportional=self.P,
            integral=self.I,
            derivative=self.D,
            cls=self.__class__.__name__
        )