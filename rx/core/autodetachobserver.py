from rx.disposables import SingleAssignmentDisposable

from .observerbase import ObserverBase


class AutoDetachObserver(ObserverBase):

    def __init__(self, observer):
        super(AutoDetachObserver, self).__init__()

        self._observer = observer
        self._subscription = SingleAssignmentDisposable()

    def _on_next_core(self, value):
        try:
            self._observer.on_next(value)
        except Exception as ex:
            import sys, traceback
            traceback.print_exc(file=sys.stdout)
            self.dispose()
            raise

    def _on_error_core(self, error):
        try:
            self._observer.on_error(error)
        finally:
            self.dispose()

    def _on_completed_core(self):
        try:
            self._observer.on_completed()
        finally:
            self.dispose()

    def set_disposable(self, value):
        self._subscription.disposable = value

    subscription = property(fset=set_disposable)

    def dispose(self):
        super().dispose()
        self._subscription.dispose()
