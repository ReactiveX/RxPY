from typing import Any, Callable, List, Optional, TypeVar

from reactivex import Observable, abc, typing
from reactivex.disposable import CompositeDisposable

_T = TypeVar("_T")


def do_action_(
    on_next: Optional[typing.OnNext[_T]] = None,
    on_error: Optional[typing.OnError] = None,
    on_completed: Optional[typing.OnCompleted] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    def do_action(source: Observable[_T]) -> Observable[_T]:
        """Invokes an action for each element in the observable
        sequence and invokes an action on graceful or exceptional
        termination of the observable sequence. This method can be used
        for debugging, logging, etc. of query behavior by intercepting
        the message stream to run arbitrary actions for messages on the
        pipeline.

        Examples:
            >>> do_action(send)(observable)
            >>> do_action(on_next, on_error)(observable)
            >>> do_action(on_next, on_error, on_completed)(observable)

        Args:
            on_next: [Optional] Action to invoke for each element in
                the observable sequence.
            on_error: [Optional] Action to invoke on exceptional
                termination of the observable sequence.
            on_completed: [Optional] Action to invoke on graceful
                termination of the observable sequence.

        Returns:
            An observable source sequence with the side-effecting
            behavior applied.
        """

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            def _on_next(x: _T) -> None:
                if not on_next:
                    observer.on_next(x)
                else:
                    try:
                        on_next(x)
                    except Exception as e:  # pylint: disable=broad-except
                        observer.on_error(e)

                    observer.on_next(x)

            def _on_error(exception: Exception) -> None:
                if not on_error:
                    observer.on_error(exception)
                else:
                    try:
                        on_error(exception)
                    except Exception as e:  # pylint: disable=broad-except
                        observer.on_error(e)

                    observer.on_error(exception)

            def _on_completed() -> None:
                if not on_completed:
                    observer.on_completed()
                else:
                    try:
                        on_completed()
                    except Exception as e:  # pylint: disable=broad-except
                        observer.on_error(e)

                    observer.on_completed()

            return source.subscribe(
                _on_next, _on_error, _on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return do_action


def do_(observer: abc.ObserverBase[_T]) -> Callable[[Observable[_T]], Observable[_T]]:
    """Invokes an action for each element in the observable sequence and
    invokes an action on graceful or exceptional termination of the
    observable sequence. This method can be used for debugging, logging,
    etc. of query behavior by intercepting the message stream to run
    arbitrary actions for messages on the pipeline.

    >>> do(observer)

    Args:
        observer: Observer

    Returns:
        An operator function that takes the source observable and
        returns the source sequence with the side-effecting behavior
        applied.
    """

    return do_action_(observer.on_next, observer.on_error, observer.on_completed)


def do_after_next(
    source: Observable[_T], after_next: typing.OnNext[_T]
) -> Observable[_T]:
    """Invokes an action with each element after it has been emitted downstream.
    This can be helpful for debugging, logging, and other side effects.

    after_next -- Action to invoke on each element after it has been emitted
    """

    def subscribe(
        observer: abc.ObserverBase[_T], scheduler: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        def on_next(value: _T):
            try:
                observer.on_next(value)
                after_next(value)
            except Exception as e:  # pylint: disable=broad-except
                observer.on_error(e)

        return source.subscribe(on_next, observer.on_error, observer.on_completed)

    return Observable(subscribe)


def do_on_subscribe(source: Observable[Any], on_subscribe: typing.Action):
    """Invokes an action on subscription.

    This can be helpful for debugging, logging, and other side effects
    on the start of an operation.

    Args:
        on_subscribe: Action to invoke on subscription
    """

    def subscribe(
        observer: abc.ObserverBase[Any], scheduler: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        on_subscribe()
        return source.subscribe(
            observer.on_next,
            observer.on_error,
            observer.on_completed,
            scheduler=scheduler,
        )

    return Observable(subscribe)


def do_on_dispose(source: Observable[Any], on_dispose: typing.Action):
    """Invokes an action on disposal.

     This can be helpful for debugging, logging, and other side effects
     on the disposal of an operation.

    Args:
        on_dispose: Action to invoke on disposal
    """

    class OnDispose(abc.DisposableBase):
        def dispose(self) -> None:
            on_dispose()

    def subscribe(
        observer: abc.ObserverBase[Any], scheduler: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        composite_disposable = CompositeDisposable()
        composite_disposable.add(OnDispose())
        subscription = source.subscribe(
            observer.on_next,
            observer.on_error,
            observer.on_completed,
            scheduler=scheduler,
        )
        composite_disposable.add(subscription)
        return composite_disposable

    return Observable(subscribe)


def do_on_terminate(source: Observable[Any], on_terminate: typing.Action):
    """Invokes an action on an on_complete() or on_error() event.
     This can be helpful for debugging, logging, and other side effects
     when completion or an error terminates an operation.


    on_terminate -- Action to invoke when on_complete or throw is called
    """

    def subscribe(
        observer: abc.ObserverBase[Any], scheduler: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        def on_completed():
            try:
                on_terminate()
            except Exception as err:  # pylint: disable=broad-except
                observer.on_error(err)
            else:
                observer.on_completed()

        def on_error(exception: Exception):
            try:
                on_terminate()
            except Exception as err:  # pylint: disable=broad-except
                observer.on_error(err)
            else:
                observer.on_error(exception)

        return source.subscribe(
            observer.on_next, on_error, on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


def do_after_terminate(source: Observable[Any], after_terminate: typing.Action):
    """Invokes an action after an on_complete() or on_error() event.
     This can be helpful for debugging, logging, and other side effects
     when completion or an error terminates an operation


    on_terminate -- Action to invoke after on_complete or throw is called
    """

    def subscribe(
        observer: abc.ObserverBase[Any], scheduler: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        def on_completed():
            observer.on_completed()
            try:
                after_terminate()
            except Exception as err:  # pylint: disable=broad-except
                observer.on_error(err)

        def on_error(exception: Exception) -> None:
            observer.on_error(exception)
            try:
                after_terminate()
            except Exception as err:  # pylint: disable=broad-except
                observer.on_error(err)

        return source.subscribe(
            observer.on_next, on_error, on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


def do_finally(
    finally_action: typing.Action,
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Invokes an action after an on_complete(), on_error(), or disposal
    event occurs.

    This can be helpful for debugging, logging, and other side effects
    when completion, an error, or disposal terminates an operation.

    Note this operator will strive to execute the finally_action once,
    and prevent any redudant calls

    Args:
        finally_action -- Action to invoke after on_complete, on_error,
        or disposal is called
    """

    class OnDispose(abc.DisposableBase):
        def __init__(self, was_invoked: List[bool]):
            self.was_invoked = was_invoked

        def dispose(self) -> None:
            if not self.was_invoked[0]:
                finally_action()
                self.was_invoked[0] = True

    def partial(source: Observable[_T]) -> Observable[_T]:
        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            was_invoked = [False]

            def on_completed():
                observer.on_completed()
                try:
                    if not was_invoked[0]:
                        finally_action()
                        was_invoked[0] = True
                except Exception as err:  # pylint: disable=broad-except
                    observer.on_error(err)

            def on_error(exception: Exception):
                observer.on_error(exception)
                try:
                    if not was_invoked[0]:
                        finally_action()
                        was_invoked[0] = True
                except Exception as err:  # pylint: disable=broad-except
                    observer.on_error(err)

            composite_disposable = CompositeDisposable()
            composite_disposable.add(OnDispose(was_invoked))
            subscription = source.subscribe(
                observer.on_next, on_error, on_completed, scheduler=scheduler
            )
            composite_disposable.add(subscription)

            return composite_disposable

        return Observable(subscribe)

    return partial


__all__ = [
    "do_",
    "do_action_",
    "do_after_next",
    "do_finally",
    "do_on_dispose",
    "do_on_subscribe",
    "do_on_terminate",
    "do_after_terminate",
]
