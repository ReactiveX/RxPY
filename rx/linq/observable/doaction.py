from rx.core import Observer, Observable, AnonymousObservable
from rx.internal import extensionmethod


@extensionmethod(Observable, alias="tap")
def do_action(self, on_next=None, on_error=None, on_completed=None,
              observer=None):
    """Invokes an action for each element in the observable sequence and
    invokes an action upon graceful or exceptional termination of the
    observable sequence. This method can be used for debugging, logging,
    etc. of query behavior by intercepting the message stream to run
    arbitrary actions for messages on the pipeline.

    1 - observable.do_action(observer)
    2 - observable.do_action(on_next)
    3 - observable.do_action(on_next, on_error)
    4 - observable.do_action(on_next, on_error, on_completed)

    observer -- [Optional] Observer, or ...
    on_next -- [Optional] Action to invoke for each element in the
        observable sequence.
    on_error -- [Optional] Action to invoke upon exceptional termination
        of the observable sequence.
    on_completed -- [Optional] Action to invoke upon graceful termination
        of the observable sequence.

    Returns the source sequence with the side-effecting behavior applied.
    """

    source = self

    if isinstance(observer, Observer):
        on_next = observer.on_next
        on_error = observer.on_error
        on_completed = observer.on_completed
    elif isinstance(on_next, Observer):
        on_error = on_next.on_error
        on_completed = on_next.on_completed
        on_next = on_next.on_next

    def subscribe(observer):
        def _on_next(x):
            try:
                on_next(x)
            except Exception as e:
                observer.on_error(e)

            observer.on_next(x)

        def _on_error(exception):
            if not on_error:
                observer.on_error(exception)
            else:
                try:
                    on_error(exception)
                except Exception as e:
                    observer.on_error(e)

                observer.on_error(exception)

        def _on_completed():
            if not on_completed:
                observer.on_completed()
            else:
                try:
                    on_completed()
                except Exception as e:
                    observer.on_error(e)

                observer.on_completed()
        return source.subscribe(_on_next, _on_error, _on_completed)
    return AnonymousObservable(subscribe)
