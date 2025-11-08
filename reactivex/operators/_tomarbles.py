from typing import Any

from reactivex import Observable, abc
from reactivex.scheduler import NewThreadScheduler
from reactivex.typing import RelativeTime

new_thread_scheduler = NewThreadScheduler()


def to_marbles(
    timespan: RelativeTime = 0.1, scheduler: abc.SchedulerBase | None = None
):
    def to_marbles(source: Observable[Any]) -> Observable[str]:
        """Convert an observable sequence into a marble diagram string.

        Args:
            timespan: [Optional] duration of each character in second.
                If not specified, defaults to 0.1s.
            scheduler: [Optional] The scheduler used to run the the input
                sequence on.

        Returns:
            Observable stream.
        """

        def subscribe(
            observer: abc.ObserverBase[str],
            scheduler: abc.SchedulerBase | None = None,
        ):
            scheduler = scheduler or new_thread_scheduler

            result: list[str] = []
            last = scheduler.now

            def add_timespan():
                nonlocal last

                now = scheduler.now
                diff = now - last
                last = now
                secs = scheduler.to_seconds(diff)
                timespan_ = scheduler.to_seconds(timespan)
                dashes = "-" * int((secs + timespan_ / 2.0) * (1.0 / timespan_))
                result.append(dashes)

            def on_next(value: Any) -> None:
                add_timespan()
                result.append(stringify(value))

            def on_error(exception: Exception) -> None:
                add_timespan()
                result.append(stringify(exception))
                observer.on_next("".join(n for n in result))
                observer.on_completed()

            def on_completed():
                add_timespan()
                result.append("|")
                observer.on_next("".join(n for n in result))
                observer.on_completed()

            return source.subscribe(on_next, on_error, on_completed)

        return Observable(subscribe)

    return to_marbles


def stringify(value: Any) -> str:
    """Utility for stringifying an event."""
    string = str(value)
    if len(string) > 1:
        string = f"({string})"

    return string


__all__ = ["stringify"]
