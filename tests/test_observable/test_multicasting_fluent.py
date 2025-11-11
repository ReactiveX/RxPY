"""Tests for MulticastingMixin fluent API methods.

This module tests the multicasting/sharing operators fluent syntax from MulticastingMixin,
ensuring they produce identical results to the pipe-based functional syntax.
"""

import reactivex as rx
from reactivex import Observable, operators as ops


class TestShareMethodChaining:
    """Tests for share() method."""

    def test_share_equivalence(self) -> None:
        """Verify share fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3)

        fluent_result: Observable[int] = source.share()
        pipe_result: Observable[int] = source.pipe(ops.share())

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3]

    def test_share_with_chaining(self) -> None:
        """Test share with subsequent operators."""
        source: Observable[int] = rx.of(1, 2, 3)

        result: Observable[int] = (
            source.share().map(lambda x: x * 2).filter(lambda x: x > 2)
        )

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [4, 6]


class TestPublishValueMethodChaining:
    """Tests for publish_value() method."""

    def test_publish_value_without_mapper(self) -> None:
        """Verify publish_value returns ConnectableObservable."""
        source: Observable[int] = rx.of(1, 2, 3)

        fluent_result = source.publish_value(0)
        pipe_result = source.pipe(ops.publish_value(0))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        # Subscribe before connecting to get the initial value
        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        # Connect to start emission
        fluent_result.connect()
        pipe_result.connect()

        # Should get initial value (0) plus source values (1, 2, 3)
        assert fluent_values == pipe_values == [0, 1, 2, 3]

    def test_publish_value_with_mapper(self) -> None:
        """Verify publish_value with mapper."""
        source: Observable[int] = rx.of(1, 2, 3)

        def mapper(shared: Observable[int]) -> Observable[int]:
            return shared.take(2)

        fluent_result: Observable[int] = source.publish_value(0, mapper)
        pipe_result: Observable[int] = source.pipe(ops.publish_value(0, mapper))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        # Should get initial value (0) and first source value (1)
        assert fluent_values == pipe_values == [0, 1]
