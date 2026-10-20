import pytest

from reactivex import operators as ops
from reactivex.testing import ReactiveTest, TestScheduler


@pytest.mark.parametrize(
    "left_times,right_times",
    [([210, 220], [230, 240]), ([230, 240], [210, 220]), ([210, 240], [220, 230])],
)
@pytest.mark.parametrize("matches", [True, False])
def test_comparer_always_receives_source_value_first(left_times, right_times, matches):
    scheduler = TestScheduler()
    left = scheduler.create_hot_observable(
        *(ReactiveTest.on_next(t, v) for t, v in zip(left_times, ["left:1", "left:2"])),
        ReactiveTest.on_completed(300),
    )
    right = scheduler.create_hot_observable(
        *(
            ReactiveTest.on_next(t, v)
            for t, v in zip(
                right_times, ["right:1", "right:2" if matches else "right:3"]
            )
        ),
        ReactiveTest.on_completed(310),
    )
    calls = []

    def comparer(source_value, second_value):
        calls.append((source_value, second_value))
        return source_value.removeprefix("left:") == second_value.removeprefix("right:")

    result = scheduler.start(lambda: left.pipe(ops.sequence_equal(right, comparer)))
    end = 310 if matches else max(left_times[1], right_times[1])
    assert result.messages == [
        ReactiveTest.on_next(end, matches),
        ReactiveTest.on_completed(end),
    ]
    assert calls == [
        ("left:1", "right:1"),
        ("left:2", "right:2" if matches else "right:3"),
    ]


@pytest.mark.parametrize("left_time,right_time", [(210, 220), (220, 210)])
def test_comparer_exception_propagates_with_consistent_arguments(left_time, right_time):
    scheduler = TestScheduler()
    left = scheduler.create_hot_observable(ReactiveTest.on_next(left_time, "left"))
    right = scheduler.create_hot_observable(ReactiveTest.on_next(right_time, "right"))
    error = ValueError("comparison failed")
    calls = []

    def comparer(source_value, second_value):
        calls.append((source_value, second_value))
        raise error

    result = scheduler.start(lambda: left.pipe(ops.sequence_equal(right, comparer)))
    assert result.messages == [ReactiveTest.on_error(220, error)]
    assert calls == [("left", "right")]
    assert left.subscriptions == [ReactiveTest.subscribe(200, 220)]
    assert right.subscriptions == [ReactiveTest.subscribe(200, 220)]
