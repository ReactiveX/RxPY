# By design, pylint: disable=C0302
from __future__ import annotations

import asyncio
import threading
from collections.abc import Callable, Generator
from typing import Any, TypeVar, cast, overload

from reactivex import abc
from reactivex.disposable import Disposable
from reactivex.scheduler import CurrentThreadScheduler
from reactivex.scheduler.eventloop import AsyncIOScheduler

from ..observer import AutoDetachObserver
from .mixins import (
    CombinationMixin,
    ConditionalMixin,
    ErrorHandlingMixin,
    FilteringMixin,
    MathematicalMixin,
    MulticastingMixin,
    TestingMixin,
    TimeBasedMixin,
    TransformationMixin,
    UtilityMixin,
    WindowingMixin,
)

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")
_E = TypeVar("_E")
_F = TypeVar("_F")
_G = TypeVar("_G")

_T_out = TypeVar("_T_out", covariant=True)


class Observable(
    abc.ObservableBase[_T_out],
    TransformationMixin[_T_out],
    FilteringMixin[_T_out],
    CombinationMixin[_T_out],
    MathematicalMixin[_T_out],
    ConditionalMixin[_T_out],
    ErrorHandlingMixin[_T_out],
    UtilityMixin[_T_out],
    TimeBasedMixin[_T_out],
    WindowingMixin[_T_out],
    MulticastingMixin[_T_out],
    TestingMixin[_T_out],
):
    """Observable with method chaining support.

    Represents a push-style collection that supports both functional (pipe-based)
    and fluent (method chaining) styles. You can :func:`pipe <pipe>` into
    :mod:`operators <reactivex.operators>` or call operator methods directly.

    The Observable class combines all operator categories through mixins:
    - TransformationMixin: map, reduce, scan, flat_map, etc.
    - FilteringMixin: filter, take, skip, distinct, etc.
    - CombinationMixin: merge, zip, combine_latest, etc.
    - MathematicalMixin: count, sum, average, min, max
    - ConditionalMixin: default_if_empty, etc.
    - ErrorHandlingMixin: catch, retry, on_error_resume_next
    - UtilityMixin: do_action, delay, timestamp, etc.
    - TimeBasedMixin: sample, debounce, etc.
    - WindowingMixin: buffer, group_by, partition, etc.
    - MulticastingMixin: share, publish, replay, etc.
    - TestingMixin: all, some, is_empty, contains, etc.
    """

    def __init__(self, subscribe: abc.Subscription[_T_out] | None = None) -> None:
        """Creates an observable sequence object from the specified
        subscription function.

        Args:
            subscribe: [Optional] Subscription function
        """
        super().__init__()

        self.lock = threading.RLock()
        self._subscribe = subscribe

    def _subscribe_core(
        self,
        observer: abc.ObserverBase[_T_out],
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        return self._subscribe(observer, scheduler) if self._subscribe else Disposable()

    def subscribe(
        self,
        on_next: abc.ObserverBase[_T_out] | abc.OnNext[_T_out] | None | None = None,
        on_error: abc.OnError | None = None,
        on_completed: abc.OnCompleted | None = None,
        *,
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        """Subscribe an observer to the observable sequence.

        You may subscribe using an observer or callbacks, not both; if the first
        argument is an instance of :class:`Observer <..abc.ObserverBase>` or if
        it has a (callable) attribute named :code:`on_next`, then any callback
        arguments will be ignored.

        Examples:
            >>> source.subscribe()
            >>> source.subscribe(observer)
            >>> source.subscribe(observer, scheduler=scheduler)
            >>> source.subscribe(on_next)
            >>> source.subscribe(on_next, on_error)
            >>> source.subscribe(on_next, on_error, on_completed)
            >>> source.subscribe(on_next, on_error, on_completed, scheduler=scheduler)

        Args:
            observer: [Optional] The object that is to receive
                notifications.
            on_error: [Optional] Action to invoke upon exceptional termination
                of the observable sequence.
            on_completed: [Optional] Action to invoke upon graceful termination
                of the observable sequence.
            on_next: [Optional] Action to invoke for each element in the
                observable sequence.
            scheduler: [Optional] The default scheduler to use for this
                subscription.

        Returns:
            Disposable object representing an observer's subscription to
            the observable sequence. Call :code:`.dispose()` on it to unsubscribe.
        """
        if (
            isinstance(on_next, abc.ObserverBase)
            or hasattr(on_next, "on_next")
            and callable(getattr(on_next, "on_next"))
        ):
            obv = cast(abc.ObserverBase[_T_out], on_next)
            on_next = obv.on_next
            on_error = obv.on_error
            on_completed = obv.on_completed

        auto_detach_observer: AutoDetachObserver[_T_out] = AutoDetachObserver(
            on_next, on_error, on_completed
        )

        def fix_subscriber(
            subscriber: abc.DisposableBase | Callable[[], None],
        ) -> abc.DisposableBase:
            """Fixes subscriber to make sure it returns a Disposable instead
            of None or a dispose function"""

            if isinstance(subscriber, abc.DisposableBase) or hasattr(
                subscriber, "dispose"
            ):
                # Note: cast can be avoided using Protocols (Python 3.9)
                return cast(abc.DisposableBase, subscriber)

            return Disposable(subscriber)

        def set_disposable(_: abc.SchedulerBase | None = None, __: Any = None) -> None:
            try:
                subscriber = self._subscribe_core(auto_detach_observer, scheduler)
            except Exception as ex:  # By design. pylint: disable=W0703
                if not auto_detach_observer.fail(ex):
                    raise
            else:
                auto_detach_observer.subscription = fix_subscriber(subscriber)

        # Subscribe needs to set up the trampoline before for subscribing.
        # Actually, the first call to Subscribe creates the trampoline so
        # that it may assign its disposable before any observer executes
        # OnNext over the CurrentThreadScheduler. This enables single-
        # threaded cancellation
        # https://social.msdn.microsoft.com/Forums/en-US/eb82f593-9684-4e27-
        # 97b9-8b8886da5c33/whats-the-rationale-behind-how-currentthreadsche
        # dulerschedulerequired-behaves?forum=rx
        current_thread_scheduler = CurrentThreadScheduler.singleton()
        if current_thread_scheduler.schedule_required():
            current_thread_scheduler.schedule(set_disposable)
        else:
            set_disposable()

        # Hide the identity of the auto detach observer
        return Disposable(auto_detach_observer.dispose)

    @overload
    def pipe(self, __op1: Callable[[Observable[_T_out]], _A]) -> _A: ...

    @overload
    def pipe(
        self,
        __op1: Callable[[Observable[_T_out]], _A],
        __op2: Callable[[_A], _B],
    ) -> _B: ...

    @overload
    def pipe(
        self,
        __op1: Callable[[Observable[_T_out]], _A],
        __op2: Callable[[_A], _B],
        __op3: Callable[[_B], _C],
    ) -> _C: ...

    @overload
    def pipe(
        self,
        __op1: Callable[[Observable[_T_out]], _A],
        __op2: Callable[[_A], _B],
        __op3: Callable[[_B], _C],
        __op4: Callable[[_C], _D],
    ) -> _D: ...

    @overload
    def pipe(
        self,
        __op1: Callable[[Observable[_T_out]], _A],
        __op2: Callable[[_A], _B],
        __op3: Callable[[_B], _C],
        __op4: Callable[[_C], _D],
        __op5: Callable[[_D], _E],
    ) -> _E: ...

    @overload
    def pipe(
        self,
        __op1: Callable[[Observable[_T_out]], _A],
        __op2: Callable[[_A], _B],
        __op3: Callable[[_B], _C],
        __op4: Callable[[_C], _D],
        __op5: Callable[[_D], _E],
        __op6: Callable[[_E], _F],
    ) -> _F: ...

    @overload
    def pipe(
        self,
        __op1: Callable[[Observable[_T_out]], _A],
        __op2: Callable[[_A], _B],
        __op3: Callable[[_B], _C],
        __op4: Callable[[_C], _D],
        __op5: Callable[[_D], _E],
        __op6: Callable[[_E], _F],
        __op7: Callable[[_F], _G],
    ) -> _G: ...

    def pipe(self, *operators: Callable[[Any], Any]) -> Any:
        """Compose multiple operators left to right.

        Composes zero or more operators into a functional composition.
        The operators are composed from left to right. A composition of zero
        operators gives back the original source.

        Examples:
            >>> source.pipe() == source
            >>> source.pipe(f) == f(source)
            >>> source.pipe(g, f) == f(g(source))
            >>> source.pipe(h, g, f) == f(g(h(source)))

        Args:
            operators: Sequence of operators.

        Returns:
             The composed observable.
        """
        from ..pipe import pipe as pipe_

        return pipe_(self, *operators)

    def run(self, scheduler: abc.SchedulerBase | None = None) -> _T_out:
        """Run source synchronously.

        Subscribes to the observable source. Then blocks and waits for the
        observable source to either complete or error. Returns the
        last value emitted, or throws exception if any error occurred.

        Examples:
            >>> result = run(source)

        Raises:
            SequenceContainsNoElementsError: if observable completes
                (on_completed) without any values being emitted.
            Exception: raises exception if any error (on_error) occurred.

        Returns:
            The last element emitted from the observable.
        """
        from ..run import run

        return run(self, scheduler)

    def __await__(self) -> Generator[Any, None, _T_out]:
        """Awaits the given observable.

        Returns:
            The last item of the observable sequence.
        """
        from ..operators._tofuture import to_future_

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

        future: asyncio.Future[_T_out] = self.pipe(
            to_future_(scheduler=AsyncIOScheduler(loop=loop))
        )
        return future.__await__()

    def __add__(self, other: Observable[_T_out]) -> Observable[_T_out]:
        """Pythonic version of :func:`concat <reactivex.concat>`.

        Example:
            >>> zs = xs + ys

        Args:
            other: The second observable sequence in the concatenation.

        Returns:
            Concatenated observable sequence.
        """
        from reactivex import concat

        return concat(self, other)

    def __iadd__(self, other: Observable[_T_out]) -> Observable[_T_out]:
        """Pythonic use of :func:`concat <reactivex.concat>`.

        Example:
            >>> xs += ys

        Args:
            other: The second observable sequence in the concatenation.

        Returns:
            Concatenated observable sequence.
        """
        from reactivex import concat

        return concat(self, other)

    def __getitem__(self, key: slice | int) -> Observable[_T_out]:
        """
        Pythonic version of :func:`slice <reactivex.operators.slice>`.

        Slices the given observable using Python slice notation. The arguments
        to slice are `start`, `stop` and `step` given within brackets `[]` and
        separated by the colons `:`.

        It is basically a wrapper around the operators
        :func:`skip <reactivex.operators.skip>`,
        :func:`skip_last <reactivex.operators.skip_last>`,
        :func:`take <reactivex.operators.take>`,
        :func:`take_last <reactivex.operators.take_last>` and
        :func:`filter <reactivex.operators.filter>`.

        The following diagram helps you remember how slices works with streams.
        Positive numbers are relative to the start of the events, while negative
        numbers are relative to the end (close) of the stream.

        .. code::

            r---e---a---c---t---i---v---e---!
            0   1   2   3   4   5   6   7   8
           -8  -7  -6  -5  -4  -3  -2  -1   0

        Examples:
            >>> result = source[1:10]
            >>> result = source[1:-2]
            >>> result = source[1:-1:2]

        Args:
            key: Slice object

        Returns:
            Sliced observable sequence.

        Raises:
            TypeError: If key is not of type :code:`int` or :code:`slice`
        """

        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step
        else:
            start, stop, step = key, key + 1, 1

        from ..operators._slice import slice_

        return slice_(start, stop, step)(self)

    # All operator methods are provided by mixins:
    # TransformationMixin, FilteringMixin, CombinationMixin, MathematicalMixin,
    # ConditionalMixin, ErrorHandlingMixin, UtilityMixin, TimeBasedMixin,
    # WindowingMixin, MulticastingMixin, TestingMixin


__all__ = ["Observable"]
