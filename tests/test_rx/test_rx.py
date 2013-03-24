import sys
from rx import Observable

def test_rx():
	assert True

def test_returnvalue():
	xs = Observable.returnvalue(42)

	def on_next(value=None):
		assert value == 42

	xs.subscribe(on_next)

def test_range():
	xs = Observable.range(0, 1)
	
	def on_next(value=None):
		assert value == 0

	xs.subscribe(on_next)
