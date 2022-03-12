import re
import threading
from datetime import datetime, timedelta
from typing import Any, List, Mapping, Optional, Tuple, Union

from reactivex import Notification, Observable, abc, notification, typing
from reactivex.disposable import CompositeDisposable, Disposable
from reactivex.scheduler import NewThreadScheduler

new_thread_scheduler = NewThreadScheduler()

# tokens will be searched in the order below using pipe
# group of elements: match any characters surrounded by ()
pattern_group = r"(\(.*?\))"
# timespan: match one or multiple hyphens
pattern_ticks = r"(-+)"
# comma err: match any comma which is not in a group
pattern_comma_error = r"(,)"
# element: match | or # or one or more characters which are not - | # ( ) ,
pattern_element = r"(#|\||[^-,()#\|]+)"

pattern = r"|".join(
    [
        pattern_group,
        pattern_ticks,
        pattern_comma_error,
        pattern_element,
    ]
)
tokens = re.compile(pattern)


def hot(
    string: str,
    timespan: typing.RelativeTime = 0.1,
    duetime: typing.AbsoluteOrRelativeTime = 0.0,
    lookup: Optional[Mapping[Union[str, float], Any]] = None,
    error: Optional[Exception] = None,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Observable[Any]:
    _scheduler = scheduler or new_thread_scheduler

    if isinstance(duetime, datetime):
        duetime = duetime - _scheduler.now

    messages = parse(
        string,
        timespan=timespan,
        time_shift=duetime,
        lookup=lookup,
        error=error,
        raise_stopped=True,
    )

    lock = threading.RLock()
    is_stopped = False
    observers: List[abc.ObserverBase[Any]] = []

    def subscribe(
        observer: abc.ObserverBase[Any], scheduler: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        # should a hot observable already completed or on error
        # re-push on_completed/on_error at subscription time?
        if not is_stopped:
            with lock:
                observers.append(observer)

        def dispose() -> None:
            with lock:
                try:
                    observers.remove(observer)
                except ValueError:
                    pass

        return Disposable(dispose)

    def create_action(notification: Notification[Any]) -> typing.ScheduledAction[Any]:
        def action(scheduler: abc.SchedulerBase, state: Any = None) -> None:
            nonlocal is_stopped

            with lock:
                for observer in observers:
                    notification.accept(observer)

                if notification.kind in ("C", "E"):
                    is_stopped = True

        return action

    for message in messages:
        timespan, notification = message
        action = create_action(notification)

        # Don't make closures within a loop
        _scheduler.schedule_relative(timespan, action)

    return Observable(subscribe)


def from_marbles(
    string: str,
    timespan: typing.RelativeTime = 0.1,
    lookup: Optional[Mapping[Union[str, float], Any]] = None,
    error: Optional[Exception] = None,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Observable[Any]:
    messages = parse(
        string, timespan=timespan, lookup=lookup, error=error, raise_stopped=True
    )

    def subscribe(
        observer: abc.ObserverBase[Any], scheduler_: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        _scheduler = scheduler or scheduler_ or new_thread_scheduler
        disp = CompositeDisposable()

        def schedule_msg(
            message: Tuple[typing.RelativeTime, Notification[Any]]
        ) -> None:
            duetime, notification = message

            def action(scheduler: abc.SchedulerBase, state: Any = None) -> None:
                notification.accept(observer)

            disp.add(_scheduler.schedule_relative(duetime, action))

        for message in messages:
            # Don't make closures within a loop
            schedule_msg(message)

        return disp

    return Observable(subscribe)


def parse(
    string: str,
    timespan: typing.RelativeTime = 1.0,
    time_shift: typing.RelativeTime = 0.0,
    lookup: Optional[Mapping[Union[str, float], Any]] = None,
    error: Optional[Exception] = None,
    raise_stopped: bool = False,
) -> List[Tuple[typing.RelativeTime, notification.Notification[Any]]]:
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
        |  `(`   | open a group of elements sharing the same timestamp    |
        +--------+--------------------------------------------------------+
        |  `)`   | close a group of elements                              |
        +--------+--------------------------------------------------------+
        |  `,`   | separate elements in a group                           |
        +--------+--------------------------------------------------------+
        | space  | used to align multiple diagrams, does not advance time |
        +--------+--------------------------------------------------------+

    In a group of elements, the position of the initial `(` determines the
    timestamp at which grouped elements will be emitted. E.g. `--(12,3,4)--`
    will emit 12, 3, 4 at 2 * timespan and then advance virtual time
    by 8 * timespan.

    Examples:
        >>> parse("--1--(2,3)-4--|")
        >>> parse("a--b--c-", lookup={'a': 1, 'b': 2, 'c': 3})
        >>> parse("a--b---#", error=ValueError("foo"))

    Args:
        string: String with marble diagram

        timespan: [Optional] duration of each character in second.
            If not specified, defaults to 0.1s.

        lookup: [Optional] dict used to convert an element into a specified
            value. If not specified, defaults to {}.

        time_shift: [Optional] time used to delay every elements.
            If not specified, defaults to 0.0s.

        error: [Optional] exception that will be use in place of the # symbol.
            If not specified, defaults to Exception('error').

        raise_finished: [optional] raise ValueError if elements are
            declared after on_completed or on_error symbol.

    Returns:
        A list of messages defined as a tuple of (timespan, notification).

    """

    error_ = error or Exception("error")
    lookup_ = lookup or {}

    if isinstance(timespan, timedelta):
        timespan = timespan.total_seconds()
    if isinstance(time_shift, timedelta):
        time_shift = time_shift.total_seconds()

    string = string.replace(" ", "")

    # try to cast a string to an int, then to a float
    def try_number(element: str) -> Union[float, str]:
        try:
            return int(element)
        except ValueError:
            try:
                return float(element)
            except ValueError:
                return element

    def map_element(
        time: typing.RelativeTime, element: str
    ) -> Tuple[typing.RelativeTime, Notification[Any]]:
        if element == "|":
            return (time, notification.OnCompleted())
        elif element == "#":
            return (time, notification.OnError(error_))
        else:
            value = try_number(element)
            value = lookup_.get(value, value)
            return (time, notification.OnNext(value))

    is_stopped = False

    def check_stopped(element: str) -> None:
        nonlocal is_stopped
        if raise_stopped:
            if is_stopped:
                raise ValueError("Elements cannot be declared after a # or | symbol.")

            if element in ("#", "|"):
                is_stopped = True

    iframe = 0
    messages: List[Tuple[typing.RelativeTime, Notification[Any]]] = []

    for results in tokens.findall(string):
        timestamp = iframe * timespan + time_shift
        group, ticks, comma_error, element = results

        if group:
            elements = group[1:-1].split(",")
            for elm in elements:
                check_stopped(elm)
            grp_messages = [
                map_element(timestamp, elm) for elm in elements if elm != ""
            ]
            messages.extend(grp_messages)
            iframe += len(group)

        if ticks:
            iframe += len(ticks)

        if comma_error:
            raise ValueError("Comma is only allowed in group of elements.")

        if element:
            check_stopped(element)
            message = map_element(timestamp, element)
            messages.append(message)
            iframe += len(element)

    return messages
