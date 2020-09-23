from threading import RLock
from typing import Optional, List

from rx import from_future
from rx.core import Observable, typing
from rx.disposable import CompositeDisposable, SingleAssignmentDisposable
from rx.internal.concurrency import synchronized
from rx.internal.utils import is_future


# pylint: disable=redefined-builtin

def _zip(*args: Observable) -> Observable:
    """Merges the specified observable sequences into one observable
    sequence by creating a tuple whenever all of the
    observable sequences have produced an element at a corresponding
    index.

    Example:
        >>> res = zip(obs1, obs2)

    Args:
        args: Observable sources to zip.

    Returns:
        An observable sequence containing the result of combining
        elements of the sources as tuple.
    """

    sources = list(args)

    def subscribe(observer: typing.Observer,
                  scheduler: Optional[typing.Scheduler] = None) -> CompositeDisposable:
        n = len(sources)
        queues: List[List] = [[] for _ in range(n)]
        lock = RLock()

        @synchronized(lock)
        def next(i):
            if all([len(q) for q in queues]):
                try:
                    queued_values = [x.pop(0) for x in queues]
                    res = tuple(queued_values)
                except Exception as ex:  # pylint: disable=broad-except
                    observer.on_error(ex)
                    return

                observer.on_next(res)

        subscriptions = [None] * n

        def func(i):
            source = sources[i]
            sad = SingleAssignmentDisposable()
            source = from_future(source) if is_future(source) else source

            def on_next(x):
                queues[i].append(x)
                next(i)

            sad.disposable = source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)
            subscriptions[i] = sad

        for idx in range(n):
            func(idx)
        return CompositeDisposable(subscriptions)

    return Observable(subscribe)
