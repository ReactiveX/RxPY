from .abstractobserver import AbstractObserver

class AnonymousObserver(AbstractObserver):
    def __init__(self, on_next, on_error, on_completed):
        super(AnonymousObserver, self).__init__()
        self._next = on_next
        self._error = on_error
        self._completed = on_completed
    