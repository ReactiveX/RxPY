from typing import Callable

import rx
from rx import Observable


def _fork_join(*args: Observable) -> Callable[[Observable], Observable]:
    def fork_join(source: Observable) -> Observable:
        """Wait for observables to complete and then combine last values
        they emitted into a tuple. Whenever any of that observables completes
        without emitting any value, result sequence will complete at that moment as well.

        Examples:
            >>> obs = fork_join(source)

        Returns:
            An observable sequence containing the result of combining last element from
            each source in given sequence.
        """
        return rx.fork_join(source, *args)

    return fork_join
