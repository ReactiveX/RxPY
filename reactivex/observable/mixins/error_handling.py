"""Error handling operators mixin for Observable."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Generic, TypeVar, cast

if TYPE_CHECKING:
    from reactivex.observable import Observable


_T = TypeVar("_T", covariant=True)


class ErrorHandlingMixin(Generic[_T]):
    """Mixin providing error handling operators for Observable.

    This mixin adds operators that handle errors, retries, and fallback behavior
    when observables encounter exceptions.
    """

    def _as_observable(self) -> Observable[_T]:
        """Cast mixin instance to Observable preserving type parameter.

        This is safe because this mixin is only ever used as part of the Observable
        class through multiple inheritance. At runtime, `self` in mixin methods will
        always be an Observable[_T] instance. The type checker cannot infer this
        because it analyzes mixins in isolation.

        Returns:
            The instance cast to Observable[_T] for type-safe method access.
        """
        return cast("Observable[_T]", self)

    def catch(
        self,
        handler: Observable[_T] | Callable[[Exception, Observable[_T]], Observable[_T]],
    ) -> Observable[_T]:
        """Handle errors by switching to another observable.

        Continues an observable sequence that is terminated by an exception with
        the next observable sequence.

        Examples:
            Fluent style:
            >>> result = source.catch(fallback_observable)
            >>> result = source.catch(lambda ex, src: handle_error(ex))

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.catch(fallback_observable))

        Args:
            handler: Exception handler function or a second observable sequence
                used to produce results when an error occurs.

        Returns:
            An observable sequence containing the source sequence's elements,
            followed by the elements of the handler sequence in case an exception
            occurred.

        See Also:
            - :func:`catch <reactivex.operators.catch>`
            - :meth:`retry`
            - :meth:`on_error_resume_next`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.catch(handler))

    def retry(self, retry_count: int | None = None) -> Observable[_T]:
        """Retry on error.

        Repeats the source observable sequence the specified number of times or
        until it successfully terminates.

        Examples:
            Fluent style:
            >>> result = source.retry(3)
            >>> result = source.retry()  # Retry indefinitely

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.retry(3))

        Args:
            retry_count: Number of times to retry. If not specified, retries
                indefinitely.

        Returns:
            An observable sequence producing the elements of the given sequence
            repeatedly until it terminates successfully.

        See Also:
            - :func:`retry <reactivex.operators.retry>`
            - :meth:`catch`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.retry(retry_count))

    def on_error_resume_next(self, second: Observable[_T]) -> Observable[_T]:
        """Continue with another observable on error or completion.

        Continues an observable sequence that is terminated normally or by an
        exception with the next observable sequence.

        Examples:
            Fluent style:
            >>> result = source.on_error_resume_next(fallback)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.on_error_resume_next(fallback))

        Args:
            second: Second observable sequence used to produce results after the
                first sequence terminates.

        Returns:
            An observable sequence that concatenates the first and second sequence,
            even if the first sequence terminates exceptionally.

        See Also:
            - :func:`on_error_resume_next <reactivex.operators.on_error_resume_next>`
            - :meth:`catch`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.on_error_resume_next(second))
