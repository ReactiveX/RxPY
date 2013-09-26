from .disposable import Disposable

# Single assignment
class SingleAssignmentDisposable(Disposable):
    def __init__(self):
        self.is_disposed = False
        self.current = None

    def get_disposable(self):
        #print("SingleAssignmentDisposable:get_disposable()")
        return self.current
    
    def set_disposable(self, value):
        #print("SingleAssignmentDisposable:set_disposable(%s)" % value)

        if self.current:
            raise Exception('Disposable has already been assigned')
        
        should_dispose = self.is_disposed
        if not should_dispose:
            self.current = value
        
        if should_dispose and value:
            value.dispose()

    disposable = property(get_disposable, set_disposable)
        
    def dispose(self):
        #print("SingleAssignmentDisposable:dispose()")
        old = None

        if not self.is_disposed:
            self.is_disposed = True
            old = self.current
            self.current = None
        
        if old:
            old.dispose()
