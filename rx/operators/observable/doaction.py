from rx.core import Observer, Observable, AnonymousObservable, Disposable
from rx.internal import extensionmethod
from rx.disposables import CompositeDisposable


@extensionmethod(Observable, alias="tap")
def do_action(self, send=None, throw=None, close=None,
              observer=None):
    """Invokes an action for each element in the observable sequence and
    invokes an action on graceful or exceptional termination of the
    observable sequence. This method can be used for debugging, logging,
    etc. of query behavior by intercepting the message stream to run
    arbitrary actions for messages on the pipeline.

    1 - observable.do_action(observer)
    2 - observable.do_action(send)
    3 - observable.do_action(send, throw)
    4 - observable.do_action(send, throw, close)

    observer -- [Optional] Observer, or ...
    send -- [Optional] Action to invoke for each element in the
        observable sequence.
    throw -- [Optional] Action to invoke on exceptional termination
        of the observable sequence.
    close -- [Optional] Action to invoke on graceful termination
        of the observable sequence.

    Returns the source sequence with the side-effecting behavior applied.
    """

    source = self

    if isinstance(observer, Observer):
        send = observer.send
        throw = observer.throw
        close = observer.close
    elif isinstance(send, Observer):
        throw = send.throw
        close = send.close
        send = send.send

    def subscribe(observer, scheduler=None):
        def _send(x):
            if not send:
                observer.send(x)
            else:
                try:
                    send(x)
                except Exception as e:
                    observer.throw(e)

                observer.send(x)

        def _throw(exception):
            if not throw:
                observer.throw(exception)
            else:
                try:
                    throw(exception)
                except Exception as e:
                    observer.throw(e)

                observer.throw(exception)

        def _close():
            if not close:
                observer.close()
            else:
                try:
                    close()
                except Exception as e:
                    observer.throw(e)

                observer.close()

        return source.subscribe_callbacks(_send, _throw, _close)

    return AnonymousObservable(subscribe)


@extensionmethod(Observable)
def do_after_next(self, after_next):
    """Invokes an action with each element after it has been emitted downstream.
    This can be helpful for debugging, logging, and other side effects.

    after_next -- Action to invoke on each element after it has been emitted
    """

    def subscribe(observer, scheduler=None):

        def send(value):
            try:
                observer.send(value)
                after_next(value)
            except Exception as e:
                observer.throw(e)

        return self.subscribe_callbacks(send, observer.throw, observer.close)

    return AnonymousObservable(subscribe)


@extensionmethod(Observable)
def do_on_subscribe(self, on_subscribe):
    """Invokes an action on subscription.
    This can be helpful for debugging, logging, and other side effects on the start of an operation.

    on_subscribe -- Action to invoke on subscription
    """
    def subscribe(observer, scheduler=None):
        on_subscribe()
        return self.subscribe_callbacks(observer.send, observer.throw, observer.close)

    return AnonymousObservable(subscribe)


@extensionmethod(Observable)
def do_on_dispose(self, on_dispose):
    """Invokes an action on disposal.
     This can be helpful for debugging, logging, and other side effects on the disposal of an operation.


    on_dispose -- Action to invoke on disposal
    """

    class OnDispose(Disposable):
        def dispose(self):
            on_dispose()

    def subscribe(observer, scheduler=None):
        composite_disposable = CompositeDisposable()
        composite_disposable.add(OnDispose())
        disposable = self.subscribe_callbacks(observer.send, observer.throw, observer.close)
        composite_disposable.add(disposable)
        return composite_disposable

    return AnonymousObservable(subscribe)


@extensionmethod(Observable)
def do_on_terminate(self, on_terminate):
    """Invokes an action on an on_complete() or throw() event.
     This can be helpful for debugging, logging, and other side effects when completion or an error terminates an operation.


    on_terminate -- Action to invoke when on_complete or throw is called
    """

    def subscribe(observer, scheduler=None):

        def close():
            try:
                on_terminate()
            except Exception as err:
                observer.throw(err)
            else:
                observer.close()

        def throw(exception):
            try:
                on_terminate()
            except Exception as err:
                observer.throw(err)
            else:
                observer.throw(exception)

        return self.subscribe_callbacks(observer.send, throw, close)

    return AnonymousObservable(subscribe)


@extensionmethod(Observable)
def do_after_terminate(self, after_terminate):
    """Invokes an action after an on_complete() or throw() event.
     This can be helpful for debugging, logging, and other side effects when completion or an error terminates an operation


    on_terminate -- Action to invoke after on_complete or throw is called
    """
    def subscribe(observer, scheduler=None):

        def close():
            observer.close()
            try:
                after_terminate()
            except Exception as err:
                observer.throw(err)

        def throw(exception):
            observer.throw(exception)
            try:
                after_terminate()
            except Exception as err:
                observer.throw(err)

        return self.subscribe(observer.send, throw, close)

    return AnonymousObservable(subscribe)


@extensionmethod(Observable)
def do_finally(self, finally_action):
    """Invokes an action after an on_complete(), throw(), or disposal event occurs
     This can be helpful for debugging, logging, and other side effects when completion, an error, or disposal terminates an operation.
    Note this operator will strive to execute the finally_action once, and prevent any redudant calls

    finally_action -- Action to invoke after on_complete, throw, or disposal is called
    """

    class OnDispose(Disposable):
        def __init__(self, was_invoked):
            self.was_invoked = was_invoked

        def dispose(self):
            if not self.was_invoked[0]:
                finally_action()
                self.was_invoked[0] = True

    def subscribe(observer, scheduler=None):

        was_invoked = [False]

        def close():
            observer.close()
            try:
                if not was_invoked[0]:
                    finally_action()
                    was_invoked[0] = True
            except Exception as err:
                observer.throw(err)

        def throw(exception):
            observer.throw(exception)
            try:
                if not was_invoked[0]:
                    finally_action()
                    was_invoked[0] = True
            except Exception as err:
                observer.throw(err)

        composite_disposable = CompositeDisposable()
        composite_disposable.add(OnDispose(was_invoked))
        disposable = self.subscribe_callbacks(observer.send, throw, close)
        composite_disposable.add(disposable)

        return composite_disposable

    return AnonymousObservable(subscribe)

