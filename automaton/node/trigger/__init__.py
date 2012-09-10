from util.subscriber import Subscriber
from util.rpc import RPC
import gevent
import datetime

class Clock(object):
    time = None
    output = None
    state_change = None

    def __init__(self, time, output, state):
        self.time = time
        self.output = output
        self.state_change = state
        gevent.spawn(self.run)

    def run(self):
        while True:
            now = datetime.datetime.utcnow()
            print "Now: %s" % now
            print self.time
            if now.hour == self.time[0] and now.minute == self.time[1]:
                self.output.set_state(self.state_change)

            gevent.sleep(60)



class Trigger(Subscriber):
    
    _input = None
    _min = None
    _max = None
    _output = None
    _state_change = None
    _current_state = None

    def __init__(self, input, output, min, max, state, current_state, port):
        self._input = input
        self._min = min
        self._max = max
        self._output = output
        self._state = state
        self._current_state = current_state
        super(Trigger, self).__init__(port=port, callback=self.handle_event)


    def handle_event(self, ob, **kwargs):
        state_change = self.test_change(ob)
        if not state_change == None:
            self._current_state = state_change
            self._output.set_state(state_change)

    def test_change(self, ob):
        if not self._input.type == ob.get('type'): return None
        if not self._input.interface.name == ob.get('node'): return None

        val = ob.get('value')
        if (val < self._min or val > self._max) and (self._current_state == self._state):
            return not self._state
        elif self._min <= ob.get('value') < self._max and not self._current_state == self._state:
            return self._state

        return None

    def json(self):
        return dict(
            input=self._input.type,
            min=self._min,
            max=self._max,
            output=self._output.type,
            state_change=self._state_change,
        )
