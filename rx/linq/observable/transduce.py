"""
# Transducers for RxPY:

There are several different implementations of transducers in Python. This
implementation is currently targeted for:

* http://code.sixty-north.com/python-transducers

Other implementations of transducers in Python are:

* https://github.com/cognitect-labs/transducers-python
* https://github.com/abingham/python-transducers
"""

from rx import Observable
from rx.internal import extensionmethod
from rx.anonymousobservable import AnonymousObservable

from transducer.infrastructure import Transducer


class Observing(Transducer):
    """An observing transducer"""

    def __init__(self, observer):
        self.observer = observer

    def initial(self):
        return self.observer

    def step(self, obs, input):
        return obs.on_next(input)

    def complete(self, obs):
        return obs.on_completed()


@extensionmethod(Observable)
def transduce(self, transducer):
    """Executes a transducer to transform the observable sequence.

    Keyword arguments:
    :param Transducer transducer: A transducer to execute.

    :returns: An Observable sequence containing the results from the
        transducer.
    :rtype: Observable
    """

    source = self

    def subscribe(observer):
        xform = transducer(Observing(observer))

        def on_next(v):
            print("on_next(%s)" % v)
            try:
                xform.step(observer, v)
            except Exception as e:
                print("transduce:excpetion")
                observer.on_error(e)

        def on_completed():
            print("on_completed()")
            xform.complete(observer)

        return source.subscribe(on_next, observer.on_error, on_completed)
    return AnonymousObservable(subscribe)
