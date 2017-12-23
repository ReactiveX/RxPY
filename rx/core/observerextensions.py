from typing import Callable

from .observerbase import ObserverBase
from .anonymousobserver import AnonymousObserver


def to_notifier(observer) -> Callable:
    """Creates a notification callback from an observer.

    Returns the action that forwards its input notification to the
    underlying observer."""

    def func(notifier):
        return notifier.accept(observer)
    return func


def as_observer(observer) -> ObserverBase:
    """Hides the identity of an observer.

    Returns an observer that hides the identity of the specified
    observer.
    """

    return AnonymousObserver(observer.send, observer.throw, observer.close)
