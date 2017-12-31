from rx.disposables import SingleAssignmentDisposable

from .observerbase import ObserverBase


class AutoDetachObserver(ObserverBase):

    def __init__(self, observer):
        super(AutoDetachObserver, self).__init__()

        self.observer = observer
        self.m = SingleAssignmentDisposable()

    def _send_core(self, value):
        try:
            self.observer.send(value)
        except Exception:
            self.dispose()
            raise

    def _throw_core(self, error):
        try:
            self.observer.throw(error)
        finally:
            self.dispose()

    def _close_core(self):
        try:
            self.observer.close()
        finally:
            self.dispose()

    def set_disposable(self, value):
        self.m.disposable = value

    disposable = property(fset=set_disposable)

    def dispose(self):
        super().dispose()
        self.m.dispose()
