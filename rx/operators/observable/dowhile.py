from typing import Callable, Any
from rx.core import ObservableBase, Observable


def do_while(condition: Callable[[Any], bool], source: Observable) -> ObservableBase:
    """Repeats source as long as condition holds emulating a do while loop.

    Keyword arguments:
    condition -- The condition which determines if the source
        will be repeated.

    Returns an observable {Observable} sequence which is repeated as long
    as the condition holds.
    """

    return source.concat(Observable.while_do(condition, source))