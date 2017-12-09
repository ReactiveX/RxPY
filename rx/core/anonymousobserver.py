from rx.internal import noop, default_error
from .observerbase import ObserverBase


class AnonymousObserver(ObserverBase):
    def __init__(self, send=None, throw=None, close=None):
        super(AnonymousObserver, self).__init__()

        self._next = send or noop
        self._error = throw or default_error
        self._close = close or noop

    def _send_core(self, value):
        self._next(value)

    def _throw_core(self, error):
        self._error(error)

    def _close_core(self):
        self._close()
