def noop():
   pass

# Main disposable class
class Disposable(object):
    def __init__(self, action):
        self.is_disposed = False
        self.action = action

    def dispose(self):
        if not self.is_disposed:
            self.action()
            self.isDisposed = True

    @classmethod
    def create(cls, action):
        return cls(action)

class DisposableEmpty(Disposable):
    def __init__(self):
        Disposable.__init__(self, noop)
