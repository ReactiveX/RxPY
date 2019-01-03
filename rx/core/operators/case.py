from rx import empty, defer, from_future
from rx.core import Observable
from rx.internal.utils import is_future


def case(mapper, sources, default_source=None) -> Observable:
    """Uses mapper to determine which source in sources to use.

    Examples:
        >>> res = case(mapper, { '1': obs1, '2': obs2 })
        >>> res = case(mapper, { '1': obs1, '2': obs2 }, obs0)

    Args:
        mapper -- The function which extracts the value for to test in a
            case statement.
        sources -- An object which has keys which correspond to the case
            statement labels.
        default_source -- The observable sequence or Future that will be run
            if the sources are not matched. If this is not provided, it
            defaults to rx.Observabe.empty.

    Returns:
        An observable sequence which is determined by a case statement.
    """

    default_source = default_source or empty()

    def factory(_) -> Observable:
        try:
            result = sources[mapper()]
        except KeyError:
            result = default_source

        result = from_future(result) if is_future(result) else result

        return result
    return defer(factory)
