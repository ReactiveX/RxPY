from datetime import timedelta
from rx.disposables import SingleAssignmentDisposable

def default_sub_comparer(x, y):
    return x - y

class ScheduledItem(object):
    def __init__(self, scheduler, state, action, duetime, comparer=None):
        self.scheduler = scheduler
        self.state = state
        self.action = action
        self.duetime = duetime
        self.comparer = comparer or default_sub_comparer
        self.disposable = SingleAssignmentDisposable()
    
    def invoke(self):
        self.disposable.disposable = self.invoke_core()
    
    def compare_to(self, other):
        return self.comparer(self.duetime, other.duetime)
    
    def is_cancelled(self):
        return self.disposable.is_disposed

    def invoke_core(self):
        #print("ScheduledItem:invoke_core", self.action)
        return self.action(self.scheduler, self.state)

    def __lt__(self, other):
        return self.compare_to(other) < timedelta(0)

    def __gt__(self, other):
        return self.compare_to(other) > timedelta(0)
    
    def __eq__(self, other):
        return self.compare_to(other) == timedelta(0)
