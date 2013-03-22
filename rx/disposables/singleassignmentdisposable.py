from disposable import Disposable

# Single assignment
class SingleAssignmentDisposable(Disposable):
    def __init__(self):
        self.is_disposed = False
        self.current = None

    def disposable(self, value):
        return self.get_disposable() if not value else self.set_disposable(value)

    def get_disposable(self):
        return self.current
    
    def set_disposable(self, value):
        if self.current:
            raise Exception('Disposable has already been assigned')
        
        should_dispose = self.is_disposed
        if should_dispose:
            self.current = value
        
        if should_dispose and value:
            value.dispose()
        
    def dispose(self):
        if not self.is_disposed:
            self.is_disposed = True
            old = self.current
            self.current = None
        
        if old:
            old.dispose()
