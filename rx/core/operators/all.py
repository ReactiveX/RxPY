from typing import Callable

from rx import operators as _
from rx.core import Observable
from rx.core.typing import Predicate


def _all(predicate: Predicate) -> Callable[[Observable], Observable]:  # pylint: disable=W0622

    filtering = _.filter(lambda v: not predicate(v))
    mapping = _.map(lambda b: not b)
    some = _.some()

    # pylint: disable=redefined-builtin
    def all(source: Observable) -> Observable:
        """Determines whether all elements of an observable sequence satisfy a
        condition.

        Example:
            >>> obs = all(source)

        Args:
            source -- Source observable to check.

        Returns:
            An observable sequence containing a single element determining
            whether all elements in the source sequence pass the test in the
            specified predicate.
        """

        return source.pipe(
            filtering,
            some,
            mapping
        )
    return all
