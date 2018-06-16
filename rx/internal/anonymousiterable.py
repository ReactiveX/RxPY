from .iterable import Iterable


class AnonymousIterable(Iterable):
    def __init__(self, iterator):
        self._iterator = iterator

    def __iter__(self):
        return self._iterator
