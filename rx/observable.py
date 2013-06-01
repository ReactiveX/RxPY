from .observer import Observer, AbstractObserver

class ObservableMeta(type):
    def __new__(cls, name, bases, namespace):
        assert len(bases) == 1, "Exactly one base class required"
        base = bases[0]
        for name, value in namespace.items():
            if name == "__init__":
                base.initializers.append(value)

            if not name.startswith("__"):
                setattr(base, name, value)
        return base

class Observable(object):
    """Represents a push-style collection."""

    initializers = []

    def __init__(self, subscribe):
        self._subscribe = subscribe
        
        # Run exension method initializers added by meta class
        for init in self.initializers:
            init(self, subscribe)

    def subscribe(self, on_next=None, on_error=None, on_completed=None):
        """Subscribes an observer to the observable sequence. Returns the source
        sequence whose subscriptions and unsubscriptions happen on the specified scheduler.
        
        1 - source.subscribe()
        2 - source.subscribe(observer)
        3 - source.subscribe(on_next)
        4 - source.subscribe(on_next, on_error)
        5 - source.subscribe(on_next, on_error, on_completed)
        
        Keyword arguments:
        observer_or_on_next -- [Optional] The object that is to receive notifications or an action to invoke for each element in the observable sequence.
        on_error -- [Optional] Action to invoke upon exceptional termination of the observable sequence.
        on_completed -- [Optional] Action to invoke upon graceful termination of the observable sequence.
        """
        if isinstance(on_next, AbstractObserver):
            observer = on_next
        else:
            observer = Observer(on_next, on_error, on_completed)
            
        return self._subscribe(observer)


