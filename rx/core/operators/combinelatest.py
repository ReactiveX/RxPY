from typing import Any, Callable, Iterable, Union, List

import rx
from rx.core import Observable, typing


def _combine_latest(other: Union[Observable, Iterable[Observable]],
                    mapper: Callable[[Any], Any]) -> Callable[[Observable], Observable]:
    def combine_latest(source: Observable) -> Observable:
        """Merges the specified observable sequences into one
        observable sequence by using the mapper function whenever any
        of the observable sequences produces an element.

        Examples:
            >>> obs = combine_latest(source)

        Returns:
            An observable sequence containing the result of combining
            elements of the sources using the specified result mapper
            function.
        """
        sources: List[Observable] = [source]

        if isinstance(other, typing.Observable):
            sources += [other]
        else:
            sources += other

        return rx.combine_latest(sources, mapper=mapper)
    return combine_latest
