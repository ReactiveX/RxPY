# By design, pylint: disable=C0302
import types
import inspect
import threading
from typing import Any, Callable, Optional

from rx.concurrency import current_thread_scheduler

from ..disposable import Disposable
from ..autodetachobserver import AutoDetachObserver
from ..anonymousobserver import AnonymousObserver
from .. import typing, abc


class Observable(typing.Observable):
    """Observables base class.

    Represents a push-style collection and contains all operators as
    methods to allow classic Rx chaining of operators."""

    def __init__(self, source: abc.Observable = None) -> None:
        self.lock = threading.RLock()
        self.source: Optional[abc.Observable] = source

    def __add__(self, other):
        """Pythonic version of concat.

        Example:
            >>> zs = xs + ys

        Returns:
            self.concat(other)"""
        from ..operators.concat import concat
        return concat(self, other)

    def __getitem__(self, key):
        """Slices the given observable using Python slice notation. The
        arguments to slice is start, stop and step given within brackets
        [] and separated with the ':' character. It is basically a
        wrapper around the operators skip(), skip_last(), take(),
        take_last() and filter().

        This marble diagram helps you remember how slices works with
        streams. Positive numbers is relative to the start of the
        events, while negative numbers are relative to the end (close)
        of the stream.

        r---e---a---c---t---i---v---e---|
        0   1   2   3   4   5   6   7   8
       -8  -7  -6  -5  -4  -3  -2  -1   0

        Examples:
            >>> result = source[1:10]
            >>> result = source[1:-2]
            >>> result = source[1:-1:2]

        Args:
            key: Slice object

        Returns:
            A sliced observable sequence.
        """

        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step
        elif isinstance(key, int):
            start, stop, step = key, key + 1, 1
        else:
            raise TypeError("Invalid argument type.")

        from ..operators.slice import slice as slice_
        return slice_(start, stop, step)(self)

    def __iadd__(self, other):
        """Pythonic use of concat.

        Example:
            xs += ys

        Returns:
            self.concat(self, other)
        """
        from ..operators.concat import concat
        return concat(self, other)

    def _subscribe_core(self, observer: typing.Observer, scheduler: typing.Scheduler = None) -> typing.Disposable:
        return self.source.subscribe(observer, scheduler) if self.source else Disposable.empty()

    def subscribe_(self,
                   on_next: typing.OnNext = None,
                   on_error: typing.OnError = None,
                   on_completed: typing.OnCompleted = None,
                   scheduler: typing.Scheduler = None
                   ) -> typing.Disposable:
        """Subscribe callbacks to the observable sequence.

        Examples:
            >>> source.subscribe_(on_next)
            >>> source.subscribe_(on_next, on_error)
            >>> source.subscribe_(on_next, on_error, on_completed)

        Args:
            on_next: Action to invoke for each element in the observable
                sequence.
            on_error: Action to invoke upon exceptional termination of
                the observable sequence.
            on_completed: Action to invoke upon graceful termination of
                the observable sequence.
            scheduler: The scheduler to use for this subscription.

        Returns:
            Disposable object representing an observer's subscription
            to the observable sequence.
        """
        observer = AnonymousObserver(on_next, on_error, on_completed)
        return self.subscribe(observer, scheduler)

    def subscribe(self, observer: typing.Observer = None, scheduler: typing.Scheduler = None) -> typing.Disposable:
        """Subscribe an observer to the observable sequence.

        Examples:
        1 - source.subscribe()
        2 - source.subscribe(observer)

        Keyword arguments:
        observer -- [Optional] The object that is to receive
            notifications. You may subscribe using an observer or
            callbacks, not both.

        Return disposable object representing an observer's subscription
            to the observable sequence.
        """

        observer = observer or AnonymousObserver()
        assert isinstance(observer, (abc.Observer, types.GeneratorType))

        if isinstance(observer, types.GeneratorType):
            if inspect.getgeneratorstate(observer) == inspect.GEN_CREATED:
                observer.send(None)

        auto_detach_observer = AutoDetachObserver(observer)

        def fix_subscriber(subscriber):
            """Fixes subscriber to make sure it returns a Disposable instead
            of None or a dispose function"""
            if not hasattr(subscriber, "dispose"):
                subscriber = Disposable.create(subscriber)

            return subscriber

        def set_disposable(_: abc.Scheduler = None, __: Any = None):
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
        if current_thread_scheduler.schedule_required():
            current_thread_scheduler.schedule(set_disposable)
        else:
            set_disposable()

        # Hide the identity of the auto detach observer
        return Disposable.create(auto_detach_observer.dispose)

    def pipe(self, *operators: Callable[['Observable'], 'Observable']) -> 'Observable':
        """Compose multiple operators left to right.

        Composes zero or more operators into a functional composition.
        The operators are composed to right. A composition of zero
        operators gives back the original source.

        source.pipe() == source
        source.pipe(f) == f(source)
        source.pipe(g, f) == f(g(source))
        source.pipe(h, g, f) == f(g(h(source)))
        ...

        Returns the composed observable.
        """
        from ..pipe import pipe
        return pipe(*operators)(self)
