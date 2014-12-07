from rx import Lock
from .observer import Observer, AbstractObserver

class Observable(object):
    """Represents a push-style collection."""

    initializers = []

    def __init__(self, subscribe):
        self._subscribe = subscribe
        self.lock = Lock()

        # Add some instance methods here since there are class methods with the 
        # same name.
        self.amb = self._Amb__amb
        self.catch_exception = self._Catch__catch_exception
        self.concat = self._Concat__concat
        self.combine_latest = self._CombineLatest__combine_latest
        self.merge = self._Merge__merge
        self.on_error_resume_next = self._OnErrorResumeNext__on_error_resume_next
        self.repeat = self._Repeat__repeat
        self.zip = self._Zip__zip
        self.zip_array = self._ZipArray__zip_array

    def subscribe(self, on_next=None, on_error=None, on_completed=None,
                  observer=None):
        """Subscribes an observer to the observable sequence. Returns the source
        sequence whose subscriptions and unsubscriptions happen on the specified
        scheduler.

        1 - source.subscribe()
        2 - source.subscribe(observer)
        3 - source.subscribe(on_next)
        4 - source.subscribe(on_next, on_error)
        5 - source.subscribe(on_next, on_error, on_completed)

        Keyword arguments:
        on_next -- [Optional] Action to invoke for each element in the
            observable sequence.
        on_error -- [Optional] Action to invoke upon exceptional termination of
            the observable sequence.
        on_completed -- [Optional] Action to invoke upon graceful termination of
            the observable sequence.
        observer -- [Optional] The object that is to receive notifications. You
            may subscribe using an observer or callbacks, not both.

        Returns {Diposable} the source sequence whose subscriptions and
        unsubscriptions happen on the specified scheduler."""

        # Be forgiving and accept an un-named observer as first parameter
        if isinstance(on_next, AbstractObserver):
            observer = on_next
        elif not observer:
            observer = Observer(on_next, on_error, on_completed)

        return self._subscribe(observer)


