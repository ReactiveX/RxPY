from rx import Observable
from rx.internal import extends


@extends(Observable)
class Case(object):

    @classmethod
    def case(cls, selector, sources, default_source=None, scheduler=None):
        """Uses selector to determine which source in sources to use.
        There is an alias 'switch_case'.

        Example:
        1 - res = rx.Observable.case(selector, { '1': obs1, '2': obs2 })
        2 - res = rx.Observable.case(selector, { '1': obs1, '2': obs2 }, obs0)
        3 - res = rx.Observable.case(selector, { '1': obs1, '2': obs2 },
                                     scheduler=scheduler)

        Keyword arguments:
        selector -- {Function} The function which extracts the value for to
            test in a case statement.
        sources -- {Array} A object which has keys which correspond to the case
            statement labels.
        default_source-- {Observable} [Optional] The observable sequence or
            Promise that will be run if the sources are not matched. If this is
            not provided, it defaults to Rx.Observabe.empty with the specified
            scheduler.

        Returns an observable {Observable} sequence which is determined by a
        case statement.
        """

        default_source = default_source or Observable.empty(scheduler=scheduler)

        def factory():
            try:
                result = sources[selector()]
            except KeyError:
                result = default_source

            result = Observable.from_future(result)

            return result
        return Observable.defer(factory)

    # Alias
    switch_case = case