from rx.concurrency import Scheduler
from rx.observable import Observable

from rx.internal import extends

@extends(Observable)
class StartsAsync(object):


    @classmethod
    def start_async(cls, function_async):
        """Invokes the asynchronous function, surfacing the result through an
        observable sequence.

        Keyword arguments:
        function_async -- {Function} Asynchronous function which returns a
            Future to run.

        Returns {Observable} An observable sequence exposing the function's
        result value, or an exception.
        """

        try:
            future = function_async()
        except Exception as ex:
            return Observable.throw(ex)

        return Observable.from_future(future)
