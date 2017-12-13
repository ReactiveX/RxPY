from __future__ import print_function

from rx import Observable, AnonymousObservable
from rx.internal import extensionmethod


@extensionmethod(Observable)
def dump(self, name = "test"):
    """Debug method for inspecting an observable sequence

    Keyword parameters:
    name -- [Optional] A name to make it easier to match the debug output if
        you insert multiple dumps into the same observable sequence.

    Return an unmodified observable sequence
    """

    def subscribe(observer, scheduler=None):
        def send(value):
            print("{%s}-->{%s}" % (name, value))
            observer.send(value)
        def throw(ex):
            print("{%s} error -->{%s}" % (name, ex))
            observer.throw(ex)
        def close():
            print("{%s} completed" % name)
            observer.close()

        return self.subscribe_callbacks(send, throw, close)
    return AnonymousObservable(subscribe)

