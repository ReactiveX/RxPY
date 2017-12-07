from rx import AnonymousObservable, Observable
from rx.internal import extensionmethod


@extensionmethod(Observable)
def default_if_empty(self, default_value=None):
    """Returns the elements of the specified sequence or the specified value
    in a singleton sequence if the sequence is empty.

    res = obs = xs.defaultIfEmpty()
    obs = xs.defaultIfEmpty(False

    Keyword arguments:
    default_value -- The value to return if the sequence is empty. If not
        provided, this defaults to None.

    Returns an observable {Observable} sequence that contains the specified
    default value if the source is empty otherwise, the elements of the
    source itself.
    """

    source = self

    def subscribe(observer, scheduler=None):
        found = [False]

        def send(x):
            found[0] = True
            observer.send(x)

        def close():
            if not found[0]:
                observer.send(default_value)
            observer.close()

        return source.subscribe_callbacks(send, observer.throw, close, scheduler)
    return AnonymousObservable(subscribe)
