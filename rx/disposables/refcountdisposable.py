from .disposable import Disposable

class RefCountDisposable(Disposable):

    class InnerDisposable(Disposable):
        def __init__(self, disposable):
            self.disposable = disposable
            self.disposable.count += 1
            self.is_inner_disposed = False

        def dispose(self):
            if not self.disposable.is_disposed:
                if not self.is_inner_disposed:
                    self.is_inner_disposed = True
                    self.disposable.count -= 1
                    if self.disposable.count == 0 and self.disposable.is_primary_disposed:
                        self.disposable.is_disposed = True
                        self.disposable.underlying_disposable.dispose()
                    
    def __init__(self, disposable):
        self.underlying_disposable = disposable
        self.is_disposed = False
        self.is_primary_disposed = False
        self.count = 0;
    
    def dispose(self):
        if not self.is_disposed:
            if not self.is_primary_disposed:
                self.is_primary_disposed = True
                if self.count == 0:
                    self.is_disposed = True
                    self.underlying_disposable.dispose()
                
    def get_disposable(self):
        return Disposable.empty() if self.is_disposed else self.InnerDisposable(self)

    disposable = property(get_disposable)