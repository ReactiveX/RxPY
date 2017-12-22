from rx.core import ObservableBase, Observable
from rx.internal.basic import noop
from rx.subjects import AsyncSubject
from rx.disposables import CompositeDisposable
from rx.concurrency import current_thread_scheduler


class ChainObservable(ObservableBase):

    def _subscribe_core(self, observer, scheduler=None):
        g = CompositeDisposable()

        def action(scheduler, state):
            observer.send(self.head)
            g.add(self.tail.merge_all().subscribe(observer))

        g.add(current_thread_scheduler.schedule(action))
        return g

    def __init__(self, head):
        super(ChainObservable, self).__init__()
        self.head = head
        self.tail = AsyncSubject()

    def close(self):
        self.send(Observable.empty())

    def throw(self, e):
        self.send(Observable.throw(e))

    def send(self, v):
        self.tail.send(v)
        self.tail.close()


def many_select(self, selector) -> ObservableBase:
    """Comonadic bind operator. Internally projects a new observable for each
    value, and it pushes each observable into the user-defined selector function
    that projects/queries each observable into some result.

    Keyword arguments:
    selector -- {Function} A transform function to apply to each element.
    scheduler -- {Object} [Optional] Scheduler used to execute the
        operation. If not specified, defaults to the ImmediateScheduler.

    Returns an observable sequence which results from the
    comonadic bind operation.
    """

    source = self

    def factory(scheduler):
        chain = [None]

        def mapper(x):
            curr = ChainObservable(x)

            chain[0] and chain[0].send(x)
            chain[0] = curr

            return curr

        def throw(e):
            if chain[0]:
                chain[0].throw(e)

        def close():
            if chain[0]:
                chain[0].close()

        return source.map(
            mapper
        ).do_action(
            noop, throw, close
        ).map(
            selector
        )

    return Observable.defer(factory)
