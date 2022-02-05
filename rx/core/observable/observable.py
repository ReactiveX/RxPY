# By design, pylint: disable=C0302
from __future__ import annotations

import asyncio
import threading
from typing import Any, Callable, Iterable, Optional, TypeVar, Union, cast, overload

from rx.core import abc
from rx.disposable import Disposable
from rx.scheduler import CurrentThreadScheduler
from rx.scheduler.eventloop import AsyncIOScheduler

from ..observer import AutoDetachObserver

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")
_E = TypeVar("_E")
_F = TypeVar("_F")
_G = TypeVar("_G")

_T = TypeVar("_T")


class Observable(abc.ObservableBase[_T]):
    """Observable base class.

    Represents a push-style collection, which you can :func:`pipe <pipe>` into
    :mod:`operators <rx.operators>`."""

    def __init__(self, subscribe: Optional[abc.Subscription[_T]] = None) -> None:
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
        observer: abc.ObserverBase[_T],
        scheduler: Optional[abc.SchedulerBase] = None,
    ) -> abc.DisposableBase:
        return self._subscribe(observer, scheduler) if self._subscribe else Disposable()

    @overload
    def subscribe(
        self,
        observer: abc.ObserverBase[_T],
        *,
        scheduler: Optional[abc.SchedulerBase] = None,
    ) -> abc.DisposableBase:
        ...

    @overload
    def subscribe(
        self,
        observer: Optional[abc.OnNext[_T]] = None,
        *,
        scheduler: Optional[abc.SchedulerBase] = None,
    ) -> abc.DisposableBase:
        ...

    def subscribe(
        self,
        observer: Union[abc.ObserverBase[_T], abc.OnNext[_T], None] = None,
        on_error: Optional[abc.OnError] = None,
        on_completed: Optional[abc.OnCompleted] = None,
        on_next: Optional[abc.OnNext[_T]] = None,
        *,
        scheduler: Optional[abc.SchedulerBase] = None,
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
            the observable sequence.
        """
        if observer:
            if (
                isinstance(observer, abc.ObserverBase)
                or hasattr(observer, "on_next")
                and callable(getattr(observer, "on_next"))
            ):
                on_next = cast(abc.ObserverBase[_T], observer).on_next
                on_error = cast(abc.ObserverBase[_T], observer).on_error
                on_completed = cast(abc.ObserverBase[_T], observer).on_completed
            else:
                on_next = observer
        return self.subscribe_(on_next, on_error, on_completed, scheduler=scheduler)

    def subscribe_(
        self,
        on_next: Optional[abc.OnNext[_T]] = None,
        on_error: Optional[abc.OnError] = None,
        on_completed: Optional[abc.OnCompleted] = None,
        scheduler: Optional[abc.SchedulerBase] = None,
    ) -> abc.DisposableBase:
        """Subscribe callbacks to the observable sequence.

        Examples:
            >>> source.subscribe_(on_next)
            >>> source.subscribe_(on_next, on_error)
            >>> source.subscribe_(on_next, on_error, on_completed)

        Args:
            on_next: [Optional] Action to invoke for each element in the
                observable sequence.
            on_error: [Optional] Action to invoke upon exceptional termination
                of the observable sequence.
            on_completed: [Optional] Action to invoke upon graceful termination
                of the observable sequence.
            scheduler: [Optional] The scheduler to use for this subscription.

        Returns:
            Disposable object representing an observer's subscription to
            the observable sequence.
        """

        auto_detach_observer: AutoDetachObserver[_T] = AutoDetachObserver(
            on_next, on_error, on_completed
        )

        def fix_subscriber(
            subscriber: Union[abc.DisposableBase, Callable[[], None]]
        ) -> abc.DisposableBase:
            """Fixes subscriber to make sure it returns a Disposable instead
            of None or a dispose function"""

            if isinstance(subscriber, abc.DisposableBase) or hasattr(
                subscriber, "dispose"
            ):
                return subscriber

            return Disposable(subscriber)

        def set_disposable(_: Optional[abc.SchedulerBase] = None, __: Any = None):
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
    def pipe(
        self, *operators: Callable[[Observable[_T]], Observable[_A]]
    ) -> Observable[_A]:  # pylint: disable=no-self-use
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
        ...

    @overload
    def pipe(self, __op1: Callable[[Observable[_T]], _A]) -> _A:
        ...

    @overload
    def pipe(
        self,
        __op1: Callable[[Observable[_T]], _A],
        __op2: Callable[[_A], _B],
    ) -> _B:
        ...

    @overload
    def pipe(
        self,
        op1: Callable[[Observable[_T]], _A],
        op2: Callable[[_A], _B],
        op3: Callable[[_B], _C],
    ) -> _C:
        ...

    @overload
    def pipe(
        self,
        op1: Callable[[Observable[_T]], _A],
        op2: Callable[[_A], _B],
        op3: Callable[[_B], _C],
        op4: Callable[[_C], _D],
    ) -> _D:
        ...

    @overload
    def pipe(
        self,
        op1: Callable[[Observable[_T]], _A],
        op2: Callable[[_A], _B],
        op3: Callable[[_B], _C],
        op4: Callable[[_C], _D],
        op5: Callable[[_D], _E],
    ) -> _E:
        ...

    @overload
    def pipe(
        self,  # pylint: disable=function-redefined, no-self-use, too-many-arguments
        op1: Callable[[Observable[_T]], _A],
        op2: Callable[[_A], _B],
        op3: Callable[[_B], _C],
        op4: Callable[[_C], _D],
        op5: Callable[[_D], _E],
        op6: Callable[[_E], _F],
    ) -> _F:
        ...

    @overload
    def pipe(
        self,  # pylint: too-many-arguments
        op1: Callable[[Observable[_T]], _A],
        op2: Callable[[_A], _B],
        op3: Callable[[_B], _C],
        op4: Callable[[_C], _D],
        op5: Callable[[_D], _E],
        op6: Callable[[_E], _F],
        op7: Callable[[_F], _G],
    ) -> _G:
        ...

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
        from ..pipe import pipe

        return pipe(*operators)(self)

    def run(self) -> Any:
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

        return run(self)

    def __await__(self) -> Iterable[_T]:
        """Awaits the given observable.

        Returns:
            The last item of the observable sequence.
        """
        from ..operators.tofuture import to_future

        loop = asyncio.get_event_loop()
        return iter(self.pipe(to_future(scheduler=AsyncIOScheduler(loop=loop))))

    def __add__(self, other: Observable[_T]) -> Observable[_T]:
        """Pythonic version of :func:`concat <rx.concat>`.

        Example:
            >>> zs = xs + ys

        Args:
            other: The second observable sequence in the concatenation.

        Returns:
            Concatenated observable sequence.
        """
        from rx import concat

        return concat(self, other)

    def __iadd__(self, other: Observable[_T]) -> "Observable[_T]":
        """Pythonic use of :func:`concat <rx.concat>`.

        Example:
            >>> xs += ys

        Args:
            other: The second observable sequence in the concatenation.

        Returns:
            Concatenated observable sequence.
        """
        from rx import concat

        return concat(self, other)

    def __getitem__(self, key: slice) -> Observable[_T]:
        """
        Pythonic version of :func:`slice <rx.operators.slice>`.

        Slices the given observable using Python slice notation. The arguments
        to slice are `start`, `stop` and `step` given within brackets `[]` and
        separated by the colons `:`.

        It is basically a wrapper around the operators
        :func:`skip <rx.operators.skip>`,
        :func:`skip_last <rx.operators.skip_last>`,
        :func:`take <rx.operators.take>`,
        :func:`take_last <rx.operators.take_last>` and
        :func:`filter <rx.operators.filter>`.

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
        elif isinstance(key, int):
            start, stop, step = key, key + 1, 1
        else:
            raise TypeError("Invalid argument type.")

        from ..operators.slice import _slice

        return _slice(start, stop, step)(self)


__all__ = ["Observable"]
