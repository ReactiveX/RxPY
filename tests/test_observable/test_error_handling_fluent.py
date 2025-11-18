"""Tests for ErrorHandlingMixin fluent API methods.

This module tests the error handling operators fluent syntax from ErrorHandlingMixin,
ensuring they produce identical results to the pipe-based functional syntax.
"""

import reactivex as rx
from reactivex import Observable, operators as ops


class TestCatchMethodChaining:
    """Tests for catch() method."""

    def test_catch_equivalence(self) -> None:
        """Verify catch fluent and functional styles are equivalent."""
        source: Observable[int] = rx.throw(Exception("Error"))
        fallback: Observable[int] = rx.of(99)

        fluent_result: Observable[int] = source.catch(fallback)
        pipe_result: Observable[int] = source.pipe(ops.catch(fallback))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append, on_error=lambda e: None)
        pipe_result.subscribe(on_next=pipe_values.append, on_error=lambda e: None)

        assert fluent_values == pipe_values == [99]

    def test_catch_with_normal_completion(self) -> None:
        """Test catch when source completes normally."""
        source: Observable[int] = rx.of(1, 2, 3)
        fallback: Observable[int] = rx.of(99)

        result: Observable[int] = source.catch(fallback)

        values: list[int] = []
        result.subscribe(on_next=values.append, on_error=lambda e: None)

        # Should return original values since no error
        assert values == [1, 2, 3]
