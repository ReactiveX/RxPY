from typing import List, Dict, Tuple
import re
import threading
from datetime import datetime, timedelta

from rx import Observable
from rx.core import notification
from rx.disposable import Disposable
from rx.disposable import CompositeDisposable
from rx.concurrency import NewThreadScheduler
from rx.core.typing import RelativeTime, AbsoluteOrRelativeTime, Scheduler


new_thread_scheduler = NewThreadScheduler()

# tokens will be search with pipe in the order below
# group of elements: match any characters surrounding by ()
pattern_group = r"(\(.*?\))"
# timespan: match one or multiple hyphens
pattern_ticks = r"(-+)"
# comma err: match any comma which is not in a group
pattern_comma_error = r"(,)"
# element: match | or # or one or more characters which are not - | # ( ) ,
pattern_element = r"(#|\||[^-,()#\|]+)"

pattern = r'|'.join([
    pattern_group,
    pattern_ticks,
    pattern_comma_error,
    pattern_element,
    ])
tokens = re.compile(pattern)


def hot(string: str, timespan: RelativeTime = 0.1, duetime: AbsoluteOrRelativeTime = 0.0,
        lookup: Dict = None, error: Exception = None, scheduler: Scheduler = None) -> Observable:

    _scheduler = scheduler or new_thread_scheduler

    if isinstance(duetime, datetime):
        duetime = duetime - _scheduler.now

    messages = parse(
        string,
        timespan=timespan,
        time_shift=duetime,
        lookup=lookup,
        error=error,
        )

    lock = threading.RLock()
    is_stopped = False
    observers = []

    def subscribe(observer, scheduler=None):
        # should a hot observable already completed or on error
        # re-push on_completed/on_error at subscription time?
        if not is_stopped:
            with lock:
                observers.append(observer)

        def dispose():
            with lock:
                try:
                    observers.remove(observer)
                except ValueError:
                    pass

        return Disposable(dispose)

    def create_action(notification):
        def action(scheduler, state=None):
            nonlocal is_stopped

            with lock:
                for observer in observers:
                    notification.accept(observer)

                if notification.kind in ('C', 'E'):
                    is_stopped = True

        return action

    for message in messages:
        timespan, notification = message
        action = create_action(notification)

        # Don't make closures within a loop
        _scheduler.schedule_relative(timespan, action)
    return Observable(subscribe)


def from_marbles(string: str, timespan: RelativeTime = 0.1, lookup: Dict = None,
                 error: Exception = None, scheduler: Scheduler = None) -> Observable:

    disp = CompositeDisposable()
    messages = parse(string, timespan=timespan, lookup=lookup, error=error)

    def schedule_msg(message, observer, scheduler):
        timespan, notification = message

        def action(scheduler, state=None):
            notification.accept(observer)

        disp.add(scheduler.schedule_relative(timespan, action))

    def subscribe(observer, scheduler_):
        _scheduler = scheduler or scheduler_ or new_thread_scheduler

        for message in messages:

            # Don't make closures within a loop
            schedule_msg(message, observer, _scheduler)
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


def parse(string: str, timespan: RelativeTime = 1.0, time_shift: RelativeTime = 0.0, lookup: Dict = None,
          error: Exception = None) -> List[Tuple[RelativeTime, notification.Notification]]:
    """Convert a marble diagram string to a list of messages.

    Each character in the string will advance time by timespan
    (exept for space). Characters that are not special (see the table below)
    will be interpreted as a value to be emitted. numbers will be cast
    to int or float.

    Special characters:
        +--------+--------------------------------------------------------+
        |  `-`   | advance time by timespan                               |
        +--------+--------------------------------------------------------+
        |  `#`   | on_error()                                             |
        +--------+--------------------------------------------------------+
        |  `|`   | on_completed()                                         |
        +--------+--------------------------------------------------------+
        |  `(`   | open a group of marbles sharing the same timestamp     |
        +--------+--------------------------------------------------------+
        |  `)`   | close a group of marbles                               |
        +--------+--------------------------------------------------------+
        |  `,`   | separate elements in a group                           |
        +--------+--------------------------------------------------------+
        | space  | used to align multiple diagrams, does not advance time |
        +--------+--------------------------------------------------------+

    In a group of marbles, the position of the initial `(` determines the
    timestamp at which grouped marbles will be emitted. E.g. `--(abc)--` will
    emit a, b, c at 2 * timespan and then advance virtual time by 5 * timespan.

    Examples:
        >>> from_marbles("--1--(2,3)-4--|")
        >>> from_marbles("a--b--c-", lookup={'a': 1, 'b': 2, 'c': 3})
        >>> from_marbles("a--b---#", error=ValueError("foo"))

    Args:
        string: String with marble diagram

        timespan: [Optional] duration of each character in second.
            If not specified, defaults to 0.1s.

        lookup: [Optional] dict used to convert a marble into a specified
            value. If not specified, defaults to {}.

        time_shift: [Optional] time used to delay every elements.
            If not specified, defaults to 0.0s.

        error: [Optional] exception that will be use in place of the # symbol.
            If not specified, defaults to Exception('error').

    Returns:
        A list of messages defined as a tuple of (timespan, notification).

    """

    error = error or Exception('error')
    lookup = lookup or {}

    if isinstance(timespan, timedelta):
        timespan = timespan.total_seconds()
    if isinstance(time_shift, timedelta):
        time_shift = time_shift.total_seconds()

    string = string.replace(' ', '')

    # try to cast a string to an int, then to a float
    def try_number(element):
        try:
            return int(element)
        except ValueError:
            try:
                return float(element)
            except ValueError:
                return element

    def map_element(time, element):
        if element == '|':
            return (time, notification.OnCompleted())
        elif element == '#':
            return (time, notification.OnError(error))
        else:
            value = try_number(element)
            value = lookup.get(value, value)
            return (time, notification.OnNext(value))

    iframe = 0
    messages = []
    for results in tokens.findall(string):
        timestamp = iframe * timespan + time_shift
        group, ticks, comma_error, element = results

        if group:
            elements = group[1:-1].split(',')
            grp_messages = [map_element(timestamp, elm) for elm in elements if elm !='']
            messages.extend(grp_messages)
            kinds = [m[1].kind for m in grp_messages]
            if 'E' in kinds or 'C' in kinds:
                break
            iframe += len(group)

        if ticks:
            iframe += len(ticks)

        if comma_error:
            raise ValueError("Comma is only allowed in group of elements.")

        if element:
            message = map_element(timestamp, element)
            messages.append(message)
            kind = message[1].kind
            if kind == 'E' or kind == 'C':
                break
            iframe += len(element)

    return messages
