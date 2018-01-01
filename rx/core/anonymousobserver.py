from rx.internal import noop, default_error
from .observerbase import ObserverBase


class AnonymousObserver(ObserverBase):
    def __init__(self, send=None, throw=None, close=None):
        super().__init__()

        self._send_core = send or noop
        self._throw_core = throw or default_error
        self._close_core = close or noop

    def _send_core(self, value):
        raise NotImplementedError

    def _throw_core(self, error):
        raise NotImplementedError

    def _close_core(self):
        raise NotImplementedError


class NoopObserver(ObserverBase):
    def _send_core(self, value):
        pass

    def _throw_core(self, error):
        pass

    def _close_core(self):
        pass
