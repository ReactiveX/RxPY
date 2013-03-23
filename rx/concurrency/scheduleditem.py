from rx.disposables import SingleAssignmentDisposable

def defaultSubComparer(x, y):
    return x - y

class ScheduledItem(object):
    def __init__(self, scheduler, state, action, duetime, comparer=None):
        self.scheduler = scheduler
        self.state = state
        self.action = action
        self.duetime = duetime
        self.comparer = comparer or defaultSubComparer
        self.disposable = SingleAssignmentDisposable()
    
    def invoke(self):
        self.disposable.disposable(self.invoke_core())
    
    def compare_to(self, other):
        return self.comparer(self.duetime, other.duetime)
    
    def is_cancelled(self):
        return self.disposable.is_disposed

    def invoke_core(self):
        print("ScheduledItem:invoke_core", self.action)
        return self.action(self.scheduler, self.state)
