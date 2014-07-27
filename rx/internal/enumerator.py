import six

class Enumerator(object):
    """For Python we just wrap the generator"""
    
    def __init__(self, next):
        self.generator = next
    
    def __next__(self):
        return six.next(self.generator)

    # Python 2.7
    next = __next__
