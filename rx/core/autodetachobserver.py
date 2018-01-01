from rx.disposables import SingleAssignmentDisposable

from .observerbase import ObserverBase


class AutoDetachObserver(ObserverBase):

    def __init__(self, observer):
        super(AutoDetachObserver, self).__init__()

        self._observer = observer
        self._subscription = SingleAssignmentDisposable()

    def _send_core(self, value):
        try:
            self._observer.send(value)
        except Exception:
            self.dispose()
            raise

    def _throw_core(self, error):
        try:
            self._observer.throw(error)
        finally:
            self.dispose()

    def _close_core(self):
        try:
            self._observer.close()
        finally:
            self.dispose()

    def set_disposable(self, value):
        self._subscription.disposable = value

    subscription = property(fset=set_disposable)

    def dispose(self):
        super().dispose()
        self._subscription.dispose()
