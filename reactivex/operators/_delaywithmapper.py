from typing import Any, Callable, Optional, TypeVar, Union

from reactivex import Observable, abc, typing
from reactivex.disposable import (
    CompositeDisposable,
    SerialDisposable,
    SingleAssignmentDisposable,
)

_T = TypeVar("_T")


def delay_with_mapper_(
    subscription_delay: Union[
        Observable[Any],
        typing.Mapper[Any, Observable[Any]],
        None,
    ] = None,
    delay_duration_mapper: Optional[typing.Mapper[_T, Observable[Any]]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    def delay_with_mapper(source: Observable[_T]) -> Observable[_T]:
        """Time shifts the observable sequence based on a subscription
        delay and a delay mapper function for each element.

        Examples:
            >>> obs = delay_with_selector(source)

        Args:
            subscription_delay: [Optional] Sequence indicating the
                delay for the subscription to the source.
            delay_duration_mapper: [Optional] Selector function to
                retrieve a sequence indicating the delay for each given
                element.

        Returns:
            Time-shifted observable sequence.
        """
        sub_delay: Optional[Observable[Any]] = None
        mapper: Optional[typing.Mapper[Any, Observable[Any]]] = None

        if isinstance(subscription_delay, abc.ObservableBase):
            mapper = delay_duration_mapper
            sub_delay = subscription_delay
        else:
            mapper = subscription_delay

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            delays = CompositeDisposable()
            at_end = [False]

            def done():
                if at_end[0] and delays.length == 0:
                    observer.on_completed()

            subscription = SerialDisposable()

            def start():
                def on_next(x: _T) -> None:
                    try:
                        assert mapper
                        delay = mapper(x)
                    except Exception as error:  # pylint: disable=broad-except
                        observer.on_error(error)
                        return

                    d = SingleAssignmentDisposable()
                    delays.add(d)

                    def on_next(_: Any) -> None:
                        observer.on_next(x)
                        delays.remove(d)
                        done()

                    def on_completed() -> None:
                        observer.on_next(x)
                        delays.remove(d)
                        done()

                    d.disposable = delay.subscribe(
                        on_next, observer.on_error, on_completed, scheduler=scheduler
                    )

                def on_completed() -> None:
                    at_end[0] = True
                    subscription.dispose()
                    done()

                subscription.disposable = source.subscribe(
                    on_next, observer.on_error, on_completed, scheduler=scheduler
                )

            if not sub_delay:
                start()
            else:
                subscription.disposable = sub_delay.subscribe(
                    lambda _: start(), observer.on_error, start
                )

            return CompositeDisposable(subscription, delays)

        return Observable(subscribe)

    return delay_with_mapper


__all__ = ["delay_with_mapper_"]
