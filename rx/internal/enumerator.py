class Enumerator(object):
    def __init__(self, next):
        self._next = next;

    def next(self):
        return self._next()

    def __next__(self):
    	return self._next()
