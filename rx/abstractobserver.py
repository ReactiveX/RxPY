# Abstract Observer
class AbstractObserver(object):
    def __init__(self):
        self.is_stopped = False

    def on_next(self, value):
        if not self.is_stopped:
            self.next(value)

    def on_error(self, error):
        if not self.is_stopped:
            self.is_stopped = True
            self.error(error)
    
    def on_completed(self):
        if not self.is_stopped:
            self.isStopped = True
            self.completed()
    
    def dispose(self):
        print ("AbstractObserver:dispose()")
        self.is_stopped = True
    
    def fail(self):
        if not self.is_stopped:
            self.is_stopped = True
            self.error(True)
            return True

        return False