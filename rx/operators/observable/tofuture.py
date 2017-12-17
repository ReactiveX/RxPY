import rx
from rx.core import ObservableBase
from rx.internal import extensionmethod


@extensionmethod(ObservableBase)
def to_future(self, future_ctor=None):
    """Converts an existing observable sequence to a Future

    Example:
    future = rx.Observable.return_value(42).to_future(trollius.Future);

    With config:
    rx.config["Future"] = trollius.Future
    future = rx.Observable.return_value(42).to_future()

    future_ctor -- {Function} [Optional] The constructor of the future.
        If not provided, it looks for it in rx.config.Future.

    Returns {Future} An future with the last value from the observable
    sequence.
    """

    future_ctor = future_ctor or rx.config.get("Future")
    if not future_ctor:
        raise Exception('Future type not provided nor in rx.config.Future')

    source = self

    future = future_ctor()

    value = [None]
    has_value = [False]

    def send(v):
        value[0] = v
        has_value[0] = True

    def throw(err):
        future.set_exception(err)

    def close():
        if has_value[0]:
            future.set_result(value[0])

    source.subscribe_callbacks(send, throw, close)

    # No cancellation can be done
    return future


@extensionmethod(ObservableBase)
def __await__(self):
    """Awaits the given observable
    :returns: The last item of the observable sequence.
    :rtype: Any
    :raises TypeError: If key is not of type int or slice
    """
    return iter(self.to_future())

