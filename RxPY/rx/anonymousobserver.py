from .abstractobserver import AbstractObserver

class AnonymousObserver(AbstractObserver):
    def __init__(self, on_next, on_error, on_completed):
        super(AnonymousObserver, self).__init__()
        self._on_next = on_next
        self._on_error = on_error
        self._on_completed = on_completed
    
    def next(self, value):
        self._on_next(value)
    
    def error(self, exception):
        self._on_error(exception)
    
    def completed(self):
        self._on_completed()
