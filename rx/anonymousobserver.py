from rx.internal import noop, default_error
from .observerbase import ObserverBase


class AnonymousObserver(ObserverBase):
    def __init__(self, on_next=None, on_error=None, on_completed=None):
        super(AnonymousObserver, self).__init__()

        self._next = on_next or noop
        self._error = on_error or default_error
        self._completed = on_completed or noop
