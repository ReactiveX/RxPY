from rx.core import ObservableBase, Observable


def case(selector, sources, default_source=None) -> ObservableBase:
    """Uses selector to determine which source in sources to use.

    Example:
    1 - res = rx.Observable.case(selector, { '1': obs1, '2': obs2 })
    2 - res = rx.Observable.case(selector, { '1': obs1, '2': obs2 }, obs0)

    Keyword arguments:
    selector -- The function which extracts the value for to test in a
        case statement.
    sources -- An object which has keys which correspond to the case
        statement labels.
    default_source -- The observable sequence or Future that will be run
        if the sources are not matched. If this is not provided, it
        defaults to rx.Observabe.empty.

    Returns an observable sequence which is determined by a case statement.
    """

    default_source = default_source or Observable.empty()

    def factory(_) -> ObservableBase:
        try:
            result = sources[selector()]
        except KeyError:
            result = default_source

        result = Observable.from_future(result)

        return result
    return Observable.defer(factory)
