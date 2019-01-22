from typing import Any, Callable, Iterable, Union, List

import rx
from rx.core import Observable, typing


def _combine_latest(other: Union[Observable, Iterable[Observable]],
                    ) -> Callable[[Observable], Observable]:
    def combine_latest(source: Observable) -> Observable:
        """Merges the specified observable sequences into one
        observable sequence by creating a tuple whenever any
        of the observable sequences produces an element.

        Examples:
            >>> obs = combine_latest(source)

        Returns:
            An observable sequence containing the result of combining
            elements of the sources into a tuple.
        """
        sources: List[Observable] = [source]

        if isinstance(other, typing.Observable):
            sources += [other]
        else:
            sources += other

        return rx.combine_latest(sources)
    return combine_latest
