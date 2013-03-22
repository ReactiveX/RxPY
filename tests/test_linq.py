import sys
from linq import Enumerable

def test():
	assert True

def test_from():
	a = Enumerable(iter([]))
	b = list(a)
	assert len(b) == 0
	
	a = Enumerable(iter([1,2,3]))
	b = list(a)
	assert len(b) == 3
	assert(b[0] == 1)
	assert(b[1] == 2)
	assert(b[2] == 3)

def test_range():
	a = Enumerable.range(1,3)
	b = list(a)
	assert len(b) == 3
	assert(b[0] == 1)
	assert(b[1] == 2)
	assert(b[2] == 3)

def test_repeat():
	a = Enumerable.repeat(123,0)
	b = list(a)
	assert len(b) == 0
	
	a = Enumerable.repeat(123,3)
	b = list(a)
	assert len(b) == 3
	assert(b[0] == 123)
	assert(b[1] == 123)
	assert(b[2] == 123)

def test_take():
	a = Enumerable.range(1,sys.maxint).take(3)
	b = list(a)
	assert len(b) == 3
	assert(b[0] == 1)
	assert(b[1] == 2)
	assert(b[2] == 3)
	