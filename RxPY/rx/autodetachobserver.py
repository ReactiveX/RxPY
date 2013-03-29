from rx.disposables import SingleAssignmentDisposable

from .abstractobserver import AbstractObserver

class AutoDetachObserver(AbstractObserver):

    def __init__(self, observer):
        super(AutoDetachObserver, self).__init__(self)
        self.observer = observer
        self.m = SingleAssignmentDisposable()

    def next(self, value):
        try:
            self.observer.on_next(value)
        except Exception:
            pass
        else:
            self.dispose()
        
    def error(self, exn):
        try:
            self.observer.on_error(exn)
        except Exception:
            self.dispose()
        
    def completed(self):
        try:
            self.observer.on_completed()
        except Exception:
            self.dispose()
        
    def disposable(self, value):
        return self.m.disposable(value)
    
    def dispose(self):
        super(AutoDetachObserver, self).dispose()
        self.m.dispose()
    