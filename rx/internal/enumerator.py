class Enumerator(object):
    """For Python we just wrap the generator"""

    def __init__(self, next):
        self.generator = next

    def __next__(self):
        return next(self.generator)

    # Python 2.7
    next = __next__

    def __iter__(self):
        return self
