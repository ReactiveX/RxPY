from rx.internal import noop, default_error
from .observerbase import ObserverBase


class AnonymousObserver(ObserverBase):
    def __init__(self, on_next=None, on_error=None, on_completed=None):
        super().__init__()

        self._on_next_core = on_next or noop
        self._on_error_core = on_error or default_error
        self._on_completed_core = on_completed or noop

    def _on_next_core(self, value):
        raise NotImplementedError

    def _on_error_core(self, error):
        raise NotImplementedError

    def _on_completed_core(self):
        raise NotImplementedError

    def throw(self, error):
        import traceback
        traceback.print_stack()
        1/0

class NoopObserver(ObserverBase):
    def _on_next_core(self, value):
        pass

    def _on_error_core(self, error):
        pass

    def _on_completed_core(self):
        pass
