from typing import Callable, Optional

from rx.core import typing

from .observablebase import ObservableBase as Observable


class AnonymousObservable(Observable):
    """Class to create an Observable instance from a delegate-based
    implementation of the Subscribe method."""

    def __init__(self, subscribe: Callable[[typing.Observer, Optional[typing.Scheduler]], typing.Disposable]) -> None:
        """Creates an observable sequence object from the specified
        subscription function.

        Args:
            subscribe: Subscribe method implementation.
        """

        self._subscribe = subscribe
        super().__init__()

    def _subscribe_core(self, observer: typing.Observer, scheduler: typing.Scheduler = None):
        return self._subscribe(observer, scheduler)
