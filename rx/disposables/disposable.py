from rx.internal import noop

class Disposable(object):
    """Main disposable class"""
    def __init__(self, action):
        """Creates a disposable object that invokes the specified action when 
        disposed.
        
        Keyword arguments:
        dispose -- Action to run during the first call to Disposable.dispose. 
            The action is guaranteed to be run at most once.
        
        Returns the disposable object that runs the given action upon disposal.
        """
        self.is_disposed = False
        self.action = action

    def dispose(self):
        """Performs the task of cleaning up resources."""

        if not self.is_disposed:
            self.action()
            self.is_disposed = True

    @classmethod
    def empty(cls):
        return cls(noop)
        
    @classmethod
    def create(cls, action):
        return cls(action)
