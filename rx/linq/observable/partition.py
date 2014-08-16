from six import add_metaclass

from rx.linq.observable import dump
from rx import AnonymousObservable, Observable
from rx.internal import ExtensionMethod
from rx.internal.utils import adapt_call

@add_metaclass(ExtensionMethod)
class ObservablePartition(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def partition(self, predicate):
        """Returns two observables which partition the observations of the
        source by the given function. The first will trigger observations for
        those values for which the predicate returns true. The second will
        trigger observations for those values where the predicate returns false.
        The predicate is executed once for each subscribed observer. Both also
        propagate all error observations arising from the source and each
        completes when the source completes.

        Keyword arguments:
        predicate -- The function to determine which output Observable will
            trigger a particular observation.

        Returns a list of observables. The first triggers when the predicate
        returns True, and the second triggers when the predicate returns False.
        """

        published = self.publish().ref_count()
        return [
            published.where(predicate), # where does adapt_call itself
            published.where(lambda x, i: not adapt_call(predicate)(x, i))
        ]

