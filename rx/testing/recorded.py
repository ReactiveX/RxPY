def default_comparer(a, b):
    return a == b

class Recorded(object):
    def __init__(self, time, value, comparer=None):
        self.time = time
        self.value = value
        self.comparer = comparer or default_comparer
    
    def equals(self, other):
        return self.time == other.time and self.comparer(self.value, other.value)
    
    def __str__(self):
        return str(self.value) + '@' + self.time

