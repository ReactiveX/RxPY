import threading
from typing import Any, Optional

from rx.internal.exceptions import SequenceContainsNoElementsError
from rx.scheduler import NewThreadScheduler
from .observable import Observable


scheduler = NewThreadScheduler()


def run(source: Observable) -> Any:
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
    result: Any = None
    done = False

    def on_next(value: Any) -> None:
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

    source.subscribe_(on_next, on_error, on_completed, scheduler=scheduler)

    while not done:
        latch.wait()

    if exception and isinstance(exception, Exception):
        raise exception  # pylint: disable=raising-bad-type

    if not has_result:
        raise SequenceContainsNoElementsError

    return result
