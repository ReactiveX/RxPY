from .disposable import Disposable

class SerialDisposable(Disposable):
    """Multiple assignment disposable"""
    
    def __init__(self):
        self.is_disposed = False
        self.current = None

    def get_disposable(self):
        return self.current

    def set_disposable(self, value):
        should_dispose = self.is_disposed
        old = None

        if not should_dispose:
            old = self.current
            self.current = value
        
        if old:
            old.dispose()
        
        if should_dispose and value:
            value.dispose()
    
    disposable = property(get_disposable, set_disposable)

    def dispose(self):
        old = None
        if not self.is_disposed:
            self.is_disposed = True
            old = self.current
            self.current = None
        
        if old:
            old.dispose()
        
