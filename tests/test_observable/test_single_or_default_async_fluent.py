"""Tests for single_or_default_async fluent API method.

This module tests the single_or_default_async operator fluent syntax,
ensuring it produces identical results to the pipe-based functional syntax.
"""

import reactivex as rx
from reactivex import Observable, operators as ops


class TestSingleOrDefaultAsyncMethodChaining:
    """Tests for single_or_default_async() method."""

    def test_single_or_default_async_with_single_element(self) -> None:
        """Verify single_or_default_async with single element."""
        source: Observable[int] = rx.of(42)

        fluent_result: Observable[int] = source.single_or_default_async()
        pipe_result: Observable[int] = source.pipe(ops.single_or_default_async())

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [42]

    def test_single_or_default_async_with_empty_and_default(self) -> None:
        """Verify single_or_default_async returns default when empty."""
        source: Observable[int] = rx.empty()

        fluent_result: Observable[int] = source.single_or_default_async(
            has_default=True, default_value=99
        )
        pipe_result: Observable[int] = source.pipe(
            ops.single_or_default_async(has_default=True, default_value=99)
        )

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [99]

    def test_single_or_default_async_with_empty_no_default(self) -> None:
        """Verify single_or_default_async errors when empty without default."""
        source: Observable[int] = rx.empty()

        fluent_result: Observable[int] = source.single_or_default_async()
        pipe_result: Observable[int] = source.pipe(ops.single_or_default_async())

        fluent_errors: list[Exception] = []
        pipe_errors: list[Exception] = []

        fluent_result.subscribe(on_error=fluent_errors.append)
        pipe_result.subscribe(on_error=pipe_errors.append)

        assert len(fluent_errors) == len(pipe_errors) == 1
        assert type(fluent_errors[0]).__name__ == type(pipe_errors[0]).__name__

    def test_single_or_default_async_with_multiple_elements(self) -> None:
        """Verify single_or_default_async errors with multiple elements."""
        source: Observable[int] = rx.of(1, 2, 3)

        fluent_result: Observable[int] = source.single_or_default_async()
        pipe_result: Observable[int] = source.pipe(ops.single_or_default_async())

        fluent_errors: list[Exception] = []
        pipe_errors: list[Exception] = []

        fluent_result.subscribe(on_error=fluent_errors.append)
        pipe_result.subscribe(on_error=pipe_errors.append)

        assert len(fluent_errors) == len(pipe_errors) == 1
        assert "more than one element" in str(fluent_errors[0]).lower()
        assert "more than one element" in str(pipe_errors[0]).lower()

    def test_single_or_default_async_equivalence(self) -> None:
        """Verify single_or_default_async fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(5)

        fluent_result: Observable[int] = source.single_or_default_async(
            has_default=True, default_value=0
        )
        pipe_result: Observable[int] = source.pipe(
            ops.single_or_default_async(has_default=True, default_value=0)
        )

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [5]
