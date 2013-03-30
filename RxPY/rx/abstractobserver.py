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
        print ("AbstractObserver:on_completed()")
        if not self.is_stopped:
            self.is_stopped = True
            self.completed()
    
    def dispose(self):
        print ("AbstractObserver:dispose()")
        self.is_stopped = True
    
    def fail(self, exn):
        if not self.is_stopped:
            self.is_stopped = True
            self.error(exn)
            return True

        return False