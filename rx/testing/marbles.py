from typing import List
import re

from rx.core import Observable
from rx.disposable import CompositeDisposable
from rx.concurrency import NewThreadScheduler
from rx.core.notification import OnNext, OnError, OnCompleted

new_thread_scheduler = NewThreadScheduler()

_pattern = r"\(?([a-zA-Z0-9]+)\)?|(-|[xX]|\|)"
_tokens = re.compile(_pattern)

def from_marbles(string: str, timespan=0.1) -> Observable:
    """Convert a marble diagram string to an observable sequence, using
    an optional scheduler to enumerate the events.

    Special characters:
        - = Timespan of timespan seconds
        x = on_error()
        | = on_completed()

    All other characters are treated as an on_next() event at the given
    moment they are found on the string.

    Examples:
        >>> res = rx.from_marbles("1-2-3-|")
        >>> res = rx.from_marbles("1-(42)-3-|")
        >>> res = rx.from_marbles("1-2-3-x", timeout_scheduler)

    Args:
        string: String with marble diagram
        scheduler: [Optional] Scheduler to run the the input sequence
            on.

    Returns:
        The observable sequence whose elements are pulled from the
        given marble diagram string.
    """

    disp = CompositeDisposable()
    completed = [False]
    messages = []
    timedelta = [0]

    def handle_timespan(value):
        timedelta[0] += timespan

    def handle_on_next(value):
        try:
            value = int(value)
        except Exception:
            pass

        if value in ('T', 'F'):
            value = value == 'T'
        messages.append((OnNext(value), timedelta[0]))

    def handle_on_completed(value):
        messages.append((OnCompleted(), timedelta[0]))
        completed[0] = True

    def handle_on_error(value):
        messages.append((OnError(value), timedelta[0]))
        completed[0] = True

    specials = {
        '-': handle_timespan,
        'x': handle_on_error,
        'X': handle_on_error,
        '|': handle_on_completed
    }

    for groups in _tokens.findall(string):
        for token in groups:
            if token:
                func = specials.get(token, handle_on_next)
                func(token)

    if not completed[0]:
        messages.append((OnCompleted(), timedelta[0]))

    def schedule_msg(message, observer, scheduler):
        notification, timespan = message

        def action(scheduler, state=None):
            notification.accept(observer)

        disp.add(scheduler.schedule_relative(timespan, action))

    def subscribe(observer, scheduler):
        scheduler = scheduler or new_thread_scheduler

        for message in messages:
            # Don't make closures within a loop
            schedule_msg(message, observer, scheduler)
        return disp
    return Observable(subscribe)


def to_marbles(scheduler=None, timespan=0.1):
    """Convert an observable sequence into a marble diagram string

    Args:
        scheduler: [Optional] The scheduler used to run the the input
            sequence on.

    Returns:
        Observable stream.
    """
    def _to_marbles(source: Observable) -> Observable:
        def subscribe(observer, scheduler=None):
            scheduler = scheduler or new_thread_scheduler

            result: List[str] = []
            last = scheduler.now

            def add_timespan():
                nonlocal last

                now = scheduler.now
                diff = now - last
                last = now
                secs = scheduler.to_seconds(diff)
                dashes = "-" * int((secs + timespan / 2.0) * (1.0 / timespan))
                result.append(dashes)

            def on_next(value):
                add_timespan()
                result.append(stringify(value))

            def on_error(exception):
                add_timespan()
                result.append(stringify(exception))
                observer.on_next("".join(n for n in result))
                observer.on_completed()

            def on_completed():
                add_timespan()
                result.append("|")
                observer.on_next("".join(n for n in result))
                observer.on_completed()

            return source.subscribe_(on_next, on_error, on_completed)
        return Observable(subscribe)
    return _to_marbles


def stringify(value):
    """Utility for stringifying an event.
    """
    string = str(value)
    if len(string) > 1:
        string = "(%s)" % string

    return string
