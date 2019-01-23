import re
import threading

from rx.disposable import CompositeDisposable
from rx.core import AnonymousObservable, Observable
from rx.concurrency import NewThreadScheduler
from rx.core.notification import OnNext, OnError, OnCompleted

new_thread_scheduler = NewThreadScheduler()

_pattern = r"\(?([a-zA-Z0-9]+)\)?|(-|[xX]|\|)"
_tokens = re.compile(_pattern)


def from_marbles(string: str) -> Observable:
    """Convert a marble diagram string to an observable sequence, using
    an optional scheduler to enumerate the events.

    Special characters:
        - = Timespan of 100 ms
        x = on_error()
        | = on_completed()

    All other characters are treated as an on_next() event at the given
    moment they are found on the string.

    Examples:
        >>> res = rx.from_string("1-2-3-|")
        >>> res = rx.from_string("1-(42)-3-|")
        >>> res = rx.from_string("1-2-3-x", timeout_scheduler)

    Args:
        string: String with marble diagram
        scheduler: [Optional] Scheduler to run the the input sequence on.

    Returns:
        The observable sequence whose elements are pulled from the
        given marble diagram string.
    """

    disp = CompositeDisposable()
    completed = [False]
    messages = []
    timespan = [0]

    def handle_timespan(value):
        timespan[0] += 0.1

    def handle_on_next(value):
        timespan[0] += 10
        if value in ('T', 'F'):
            value = value == 'T'
        messages.append((OnNext(value), timespan[0]))

    def handle_on_completed(value):
        timespan[0] += 0.01
        messages.append((OnCompleted(), timespan[0]))
        completed[0] = True

    def handle_on_error(value):
        timespan[0] += 0.01
        messages.append((OnError(value), timespan[0]))
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
        messages.append((OnCompleted(), timespan[0]))

    def subscribe(observer, scheduler):
        for message in messages:
            notification, timespan = message

            # Don't make closures within a loop
            action = notification.accept(observer)
            disp.add(scheduler.schedule_relative(timespan, action))
        return disp
    return AnonymousObservable(subscribe)


def to_marbles(self, scheduler=None):
    """Convert an observable sequence into a marble diagram string

    Args:
        scheduler: [Optional] The scheduler used to run the the input
            sequence on.

    Returns:
        Observable stream.
    """
    source = self

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or new_thread_scheduler
        result = []
        previously = [scheduler.now]

        def add_timespan():
            now = scheduler.now
            diff = now - previously[0]
            previously[0] = now
            msecs = scheduler.to_relative(diff)
            dashes = "-" * int((msecs + 50) / 100)
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
    return AnonymousObservable(subscribe)


def to_marbles_blocking(self, scheduler=None):
    """Convert an observable sequence into a marble diagram string

    Args:
        scheduler: [Optional] The scheduler used to run the the input
            sequence on.

    Returns:
        Marble string.
    """

    latch = threading.Event()
    ret = [None]

    def on_next(value):
        ret[0] = value

    self.observable.to_marbles(scheduler=scheduler).subscribe_(on_next, close=latch.set)

    # Block until the subscription completes and then return
    latch.wait()

    return ret[0]


def stringify(value):
    """Utility for stringifying an event.
    """
    string = str(value)
    if len(string) > 1:
        string = "(%s)" % string

    return string
