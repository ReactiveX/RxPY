# By design, pylint: disable=C0302
import threading
from typing import cast, overload, Any, Callable, Optional, TypeVar

from rx.disposable import Disposable
from rx.scheduler import CurrentThreadScheduler

from ..observer import AutoDetachObserver
from .. import typing, abc

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
D = TypeVar('D')
E = TypeVar('E')
F = TypeVar('F')
G = TypeVar('G')


class Observable(typing.Observable):
    """Observable base class.

    Represents a push-style collection, which you can :func:`pipe <pipe>` into
    :mod:`operators <rx.operators>`."""

    def __init__(self,
                 subscribe: Optional[typing.SubscribeCallbacks] = None,
                 *,
                 subscribe_observer: Optional[typing.SubscribeObserver] = None
                 ) -> None:
        """Creates an observable sequence object from the given subscribe
        function.

        Note: only one of the arguments takes effect, and the first one takes
        precedence in case both are given.

        Args:
            subscribe: [Optional] Subscription function using callbacks.
            subscribe_observer: [Optional] Subscription function using an
                :class:`Observer <rx.core.typing.Observer>`.
        """

        super().__init__()

        self.lock = threading.RLock()
        self._subscribe = subscribe
        self._subscribe_observer = subscribe_observer

    def _subscribe_core(self,
                        observer: typing.Observer,
                        scheduler: Optional[typing.Scheduler] = None
                        ) -> typing.Disposable:
        if self._subscribe is not None:
            return self._subscribe(observer.on_next,
                                   observer.on_error,
                                   observer.on_completed,
                                   scheduler)

        if self._subscribe_observer is not None:
            return self._subscribe_observer(observer, scheduler)

        return Disposable()

    def subscribe(self,
                  on_next: Optional[typing.OnNext] = None,
                  on_error: Optional[typing.OnError] = None,
                  on_completed: Optional[typing.OnCompleted] = None,
                  *,
                  scheduler: Optional[typing.Scheduler] = None
                  ) -> typing.Disposable:
        """Subscribe callbacks to the observable sequence.

        Examples:
            >>> source.subscribe(on_next)
            >>> source.subscribe(on_next, on_error)
            >>> source.subscribe(on_next, on_error, on_completed)

        Args:
            on_next: [Optional] Action to invoke for each element in the
                observable sequence.
            on_error: [Optional] Action to invoke upon exceptional termination
                of the observable sequence.
            on_completed: [Optional] Action to invoke upon graceful termination
                of the observable sequence.
            scheduler: [Optional] The scheduler to use for this subscription.

        Returns:
            Disposable object representing subscription to the observable
            sequence.
        """

        auto_detach_obs = AutoDetachObserver(on_next, on_error, on_completed)

        def fix_subscriber(subscriber):
            """Fixes subscriber to make sure it returns a Disposable instead
            of None or a dispose function"""
            if not hasattr(subscriber, 'dispose'):
                subscriber = Disposable(subscriber)

            return subscriber

        def set_disposable(_: abc.Scheduler = None, __: Any = None):
            try:
                subscriber = self._subscribe_core(auto_detach_obs, scheduler)
            except Exception as ex:  # By design. pylint: disable=W0703
                if not auto_detach_obs.fail(ex):
                    raise
            else:
                auto_detach_obs.subscription = fix_subscriber(subscriber)

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
        return Disposable(auto_detach_obs.dispose)

    @overload
    def pipe(self,
             *operators: Callable[['Observable'], 'Observable']
             ) -> 'Observable':  # pylint: disable=no-self-use
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
    def pipe(self) -> 'Observable':  # pylint: disable=function-redefined, no-self-use
        ...  # pylint: disable=pointless-statement

    @overload
    def pipe(self, op1: Callable[['Observable'], A]) -> A:  # pylint: disable=function-redefined, no-self-use
        ...  # pylint: disable=pointless-statement

    @overload
    def pipe(self,  # pylint: disable=function-redefined, no-self-use
             op1: Callable[['Observable'], A],
             op2: Callable[[A], B]) -> B:
        ...  # pylint: disable=pointless-statement

    @overload
    def pipe(self,  # pylint: disable=function-redefined, no-self-use
             op1: Callable[['Observable'], A],
             op2: Callable[[A], B],
             op3: Callable[[B], C]) -> C:
        ...  # pylint: disable=pointless-statement

    @overload
    def pipe(self,  # pylint: disable=function-redefined, no-self-use
             op1: Callable[['Observable'], A],
             op2: Callable[[A], B],
             op3: Callable[[B], C],
             op4: Callable[[C], D]) -> D:
        ...  # pylint: disable=pointless-statement

    @overload
    def pipe(self,  # pylint: disable=function-redefined, no-self-use, too-many-arguments
             op1: Callable[['Observable'], A],
             op2: Callable[[A], B],
             op3: Callable[[B], C],
             op4: Callable[[C], D],
             op5: Callable[[D], E]) -> E:
        ...  # pylint: disable=pointless-statement

    @overload
    def pipe(self,  # pylint: disable=function-redefined, no-self-use, too-many-arguments
             op1: Callable[['Observable'], A],
             op2: Callable[[A], B],
             op3: Callable[[B], C],
             op4: Callable[[C], D],
             op5: Callable[[D], E],
             op6: Callable[[E], F]) -> F:
        ...  # pylint: disable=pointless-statement

    @overload
    def pipe(self,  # pylint: disable=function-redefined, no-self-use, too-many-arguments
             op1: Callable[['Observable'], A],
             op2: Callable[[A], B],
             op3: Callable[[B], C],
             op4: Callable[[C], D],
             op5: Callable[[D], E],
             op6: Callable[[E], F],
             op7: Callable[[F], G]) -> G:
        ...  # pylint: disable=pointless-statement

    # pylint: disable=function-redefined
    def pipe(self, *operators: Callable[['Observable'], Any]) -> Any:
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

    def __await__(self) -> Any:
        """Awaits the given observable.

        Returns:
            The last item of the observable sequence.
        """
        from ..operators.tofuture import _to_future
        return iter(self.pipe(_to_future()))

    def __add__(self, other) -> 'Observable':
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

    def __iadd__(self, other) -> 'Observable':
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

    def __getitem__(self, key) -> 'Observable':
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
            raise TypeError('Invalid argument type.')

        from ..operators.slice import _slice
        return _slice(start, stop, step)(self)
