
from typing import Any
from rx.core.blockingobservable import BlockingObservable


def first(source: BlockingObservable) -> Any:
    """
    Blocks until the first element emits from a BlockingObservable.

    If no item is emitted when on_completed() is called, an exception is thrown

    Note: This will block even if the underlying Observable is
    asynchronous.

    Keyword arguments:
    source -- Blocking observable sequence.

    Returns the first item to be emitted from the blocking observable.
    """
    return next(iter(source.to_iterable()))


def first_or_default(source: BlockingObservable, default_value: Any) -> Any:
    """
    Blocks until the first element emits from a BlockingObservable.

    If no item is emitted when on_completed() is called, the provided default
    value is returned instead

    Note: This will block even if the underlying Observable is
    asynchronous.

    Keyword arguments:
    source -- Blocking observable sequence.
    default_value -- Default value to use

    Returns the first item to be emitted from the blocking observable.
    """
    return next(iter(source.to_iterable()), default_value)

