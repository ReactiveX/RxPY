from typing import Generic, Optional, TypeVar

from reactivex import abc
from reactivex.disposable import CompositeDisposable, Disposable, RefCountDisposable

from .observable import Observable

_T = TypeVar("_T")
_TKey = TypeVar("_TKey")


class GroupedObservable(Generic[_TKey, _T], Observable[_T]):
    def __init__(
        self,
        key: _TKey,
        underlying_observable: Observable[_T],
        merged_disposable: Optional[RefCountDisposable] = None,
    ):
        super().__init__()
        self.key = key

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            return CompositeDisposable(
                merged_disposable.disposable if merged_disposable else Disposable(),
                underlying_observable.subscribe(observer, scheduler=scheduler),
            )

        self.underlying_observable: Observable[_T] = (
            underlying_observable if not merged_disposable else Observable(subscribe)
        )

    def _subscribe_core(
        self,
        observer: abc.ObserverBase[_T],
        scheduler: Optional[abc.SchedulerBase] = None,
    ) -> abc.DisposableBase:
        return self.underlying_observable.subscribe(observer, scheduler=scheduler)
