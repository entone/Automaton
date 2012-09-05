from util.subscriber import Subscriber
from util.rpc import RPC


class Trigger(Subscriber):
	
	_type = None
	_node = None
	_min = None
	_max = None
	_output = None
	_state_change = None
	_current_state = None
	_rpc = None
	_range = None


	def __init__(self, type, node, min, max, output, state, current_state, uri):
		self._type = type
		self._node = node
		self._min = min
		self._max = max
		self._output = output
		self._state = state
		self._current_state = current_state
		self._rpc = RPC("tcp://127.0.0.1:6666")
		super(Trigger, self).__init__(uri=uri, callback=self.handle_event)


	def handle_event(self, ob, **kwargs):
		state_change = self.test_change(ob)		
		if not state_change == None:
			actor = dict(
				id=self._output,
				node=self._node,
				state=state_change,
				method='set_output_state',
			)
			self._current_state = state_change
			self._rpc.send(actor)

	def test_change(self, ob):
		if not self._type == ob.get('type'): return None
		if not self._node == ob.get('node'): return None

		val = ob.get('value')
		if (val < self._min or val > self._max) and (self._current_state == self._state):
			return not self._state
		elif self._min <= ob.get('value') < self._max and not self._current_state == self._state:
			return self._state

		return None

