from rx.core import ObservableBase, Observable
from rx.core.typing import Mapper
from rx.internal.basic import noop
from rx.subjects import AsyncSubject
from rx.disposables import CompositeDisposable


class ChainObservable(ObservableBase):

    def _subscribe_core(self, observer, scheduler=None):
        g = CompositeDisposable()

        def action(scheduler, state):
            observer.on_next(self.head)
            g.add(self.tail.merge_all().subscribe(observer, scheduler))

        g.add(scheduler.schedule(action))
        return g

    def __init__(self, head):
        super().__init__()

        self.head = head
        self.tail = AsyncSubject()

    def on_completed(self):
        self.on_next(rx.empty())

    def on_error(self, error):
        self.on_next(rx.throw(error))

    def on_next(self, value):
        self.tail.on_next(value)
        self.tail.on_completed()


def many_select(source: ObservableBase, mapper: Mapper) -> ObservableBase:
    """Comonadic bind operator. Internally projects a new observable for each
    value, and it pushes each observable into the user-defined mapper function
    that projects/queries each observable into some result.

    Keyword arguments:
    mapper -- {Function} A transform function to apply to each element.
    scheduler -- {Object} [Optional] Scheduler used to execute the
        operation. If not specified, defaults to the ImmediateScheduler.

    Returns an observable sequence which results from the
    comonadic bind operation.
    """

    def factory(scheduler):
        chain = [None]

        def _mapper(x):
            curr = ChainObservable(x)

            chain[0] and chain[0].on_next(x)
            chain[0] = curr

            return curr

        def on_error(error):
            if chain[0]:
                chain[0].on_error(error)

        def on_completed():
            if chain[0]:
                chain[0].on_completed()

        return (source
                .map(_mapper)
                .do_action(noop, on_error, on_completed)
                .map(mapper)
               )

    return Observable.defer(factory)
