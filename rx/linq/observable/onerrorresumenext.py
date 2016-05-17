from rx.core import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable, \
    SerialDisposable
from rx.concurrency import immediate_scheduler
from rx.internal import extensionmethod, extensionclassmethod


@extensionmethod(Observable, instancemethod=True)
def on_error_resume_next(self, second):
    """Continues an observable sequence that is terminated normally or by
    an exception with the next observable sequence.

    Keyword arguments:
    second -- Second observable sequence used to produce results after the
        first sequence terminates.

    Returns an observable sequence that concatenates the first and second
    sequence, even if the first sequence terminates exceptionally.
    """

    if not second:
        raise Exception('Second observable is required')

    return Observable.on_error_resume_next([self, second])

@extensionclassmethod(Observable)
def on_error_resume_next(cls, *args):
    """Continues an observable sequence that is terminated normally or by
    an exception with the next observable sequence.

    1 - res = Observable.on_error_resume_next(xs, ys, zs)
    2 - res = Observable.on_error_resume_next([xs, ys, zs])
    3 - res = Observable.on_error_resume_next(xs, factory)

    Returns an observable sequence that concatenates the source sequences,
    even if a sequence terminates exceptionally.
    """

    if args and isinstance(args[0], list):
        sources = iter(args[0])
    else:
        sources = iter(args)

    def subscribe(observer):
        subscription = SerialDisposable()

        def action(this, state=None):
            try:
                source = next(sources)
            except StopIteration:
                observer.on_completed()
                return

            # Allow source to be a factory method taking an error
            source = source(state) if callable(source) else source
            current = Observable.from_future(source)

            d = SingleAssignmentDisposable()
            subscription.disposable = d
            d.disposable = current.subscribe(
                    observer.on_next,
                    lambda ex: this(ex),
                    this)

        cancelable = immediate_scheduler.schedule_recursive(action)
        return CompositeDisposable(subscription, cancelable)
    return AnonymousObservable(subscribe)
