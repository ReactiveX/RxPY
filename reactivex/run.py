import threading
from typing import Optional, TypeVar, cast

from reactivex.internal.exceptions import SequenceContainsNoElementsError
from reactivex.scheduler import NewThreadScheduler

from .observable import Observable

scheduler = NewThreadScheduler()

_T = TypeVar("_T")


def run(source: Observable[_T]) -> _T:
    """Run source synchronously.

    Subscribes to the observable source. Then blocks and waits for the
    observable source to either complete or error. Returns the
    last value emitted, or throws exception if any error occured.

    Examples:
        >>> result = run(source)

    Args:
        source: Observable source to run.

    Raises:
        SequenceContainsNoElementsError: if observable completes
            (on_completed) without any values being emitted.
        Exception: raises exception if any error (on_error) occured.

    Returns:
        The last element emitted from the observable.
    """
    exception: Optional[Exception] = None
    latch = threading.Event()
    has_result = False
    result: _T = cast(_T, None)
    done = False

    def on_next(value: _T) -> None:
        nonlocal result, has_result
        result = value
        has_result = True

    def on_error(error: Exception) -> None:
        nonlocal exception, done

        exception = error
        done = True
        latch.set()

    def on_completed() -> None:
        nonlocal done
        done = True
        latch.set()

    source.subscribe(on_next, on_error, on_completed, scheduler=scheduler)

    while not done:
        latch.wait()

    if exception:
        raise cast(Exception, exception)

    if not has_result:
        raise SequenceContainsNoElementsError

    return result
