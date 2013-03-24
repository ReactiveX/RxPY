import sys

class Subscription(object):
    def __init__(self, start, end):
        self.subscribe = start;
        self.unsubscribe = end or sys.maxsize

    def equals(other):
        return self.subscribe == other.subscribe and self.unsubscribe == other.unsubscribe

    def __str__(self):
        return '(' + self.subscribe + ', ' + self.unsubscribe == sys.maxsize ? 'Infinite' : self.unsubscribe + ')'

