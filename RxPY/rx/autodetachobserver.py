from rx.disposables import SingleAssignmentDisposable

from .abstractobserver import AbstractObserver

class AutoDetachObserver(AbstractObserver):

    def __init__(self, observer):
        super(AutoDetachObserver, self).__init__()
        self.observer = observer
        self.m = SingleAssignmentDisposable()

    def next(self, value):
        try:
            self.observer.on_next(value)
        except Exception:
            print ("dispose ***")
            self.dispose()
        
    def error(self, exn):
        try:
            self.observer.on_error(exn)
        except Exception:
            pass
        finally:
            self.dispose()
        
    def completed(self):
        try:
            self.observer.on_completed()
        except Exception:
            pass
        finally:
            self.dispose()
        
    def disposable(self, value):
        self.m.disposable = value
    
    def dispose(self):
        super(AutoDetachObserver, self).dispose()
        self.m.dispose()
    