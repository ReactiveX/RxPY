from six import add_metaclass

from rx import Observable, AnonymousObservable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableDump(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def dump(self, name = "test"):
        """Debug method for inspecting an observable sequence

        Keyword parameters:
        name -- [Optional] A name to make it easier to match the debug output if
            you insert multiple dumps into the same observable sequence.

        Return an unmodified observable sequence"""

        def subscribe(observer):
            def on_next(value):
                print("{%s}-->{%s}" % (name, value))
                observer.on_next(value)
            def on_error(ex):
                print("{%s} error -->{%s}" % (name, ex))
                traceback.print_exc(file=sys.stdout)
                observer.on_error(ex)
            def on_completed():
                print("{%s} completed" % name)
                observer.on_completed()

            return self.subscribe(on_next, on_error, on_completed)
        return AnonymousObservable(subscribe)

