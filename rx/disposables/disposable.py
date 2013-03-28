from rx.internal import noop

# Main disposable class
class Disposable(object):
    def __init__(self, action):
        self.is_disposed = False
        self.action = action

    def dispose(self):
        if not self.is_disposed:
            self.action()
            self.is_disposed = True

    @classmethod
    def create(cls, action):
        return cls(action)

    @classmethod
    def empty(cls):
        return cls(noop)

disposable_empty = Disposable.empty