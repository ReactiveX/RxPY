import pytest

from reactivex import never
from reactivex import operators as ops
from reactivex.subject import Subject


@pytest.mark.parametrize("side", ["left", "right"])
def test_join_duration_can_expire_during_result_notification(side):
    left = Subject()
    right = Subject()
    durations = {1: Subject(), 2: Subject()}
    received = []
    errors = []
    completed = []
    left_duration = (
        (lambda value: durations[value]) if side == "left" else (lambda _: never())
    )
    right_duration = (
        (lambda value: durations[value]) if side == "right" else (lambda _: never())
    )

    def on_next(pair):
        received.append(pair)
        durations[pair[0] if side == "left" else pair[1]].on_next(None)

    left.pipe(ops.join(right, left_duration, right_duration)).subscribe(
        on_next, errors.append, lambda: completed.append(True)
    )
    buffered, trigger = (left, right) if side == "left" else (right, left)
    buffered.on_next(1)
    buffered.on_next(2)
    trigger.on_next(3)
    trigger.on_next(4)
    left.on_completed()
    right.on_completed()
    assert received == ([(1, 3), (2, 3)] if side == "left" else [(3, 1), (3, 2)])
    assert errors == []
    assert completed == [True]


def test_group_join_window_can_close_during_right_notification():
    left = Subject()
    right = Subject()
    durations = {1: Subject(), 2: Subject()}
    received = {1: [], 2: []}
    completed = []

    def on_group(pair):
        key, window = pair

        def on_next(value):
            received[key].append(value)
            durations[key].on_next(None)

        window.subscribe(on_next, on_completed=lambda: completed.append(key))

    left.pipe(
        ops.group_join(right, lambda key: durations[key], lambda _: never())
    ).subscribe(on_group)
    left.on_next(1)
    left.on_next(2)
    right.on_next(3)
    right.on_next(4)
    assert received == {1: [3], 2: [3]}
    assert completed == [1, 2]


def test_group_join_buffered_right_can_expire_during_replay():
    left = Subject()
    right = Subject()
    durations = {1: Subject(), 2: Subject()}
    received = []

    def on_group(pair):
        def on_next(value):
            received.append(value)
            durations[value].on_next(None)

        pair[1].subscribe(on_next)

    left.pipe(
        ops.group_join(right, lambda _: never(), lambda key: durations[key])
    ).subscribe(on_group)
    right.on_next(1)
    right.on_next(2)
    left.on_next(3)
    left.on_next(4)
    assert received == [1, 2]


@pytest.mark.parametrize(
    "origin",
    ["left", "right", "left_duration", "right_duration", "left_mapper", "right_mapper"],
)
def test_group_join_error_fanout_can_close_groups(origin):
    left = Subject()
    right = Subject()
    left_durations = {1: Subject(), 2: Subject()}
    right_duration = Subject()
    error = ValueError("failed")
    received = []
    outer_errors = []

    def left_mapper(key):
        if origin == "left_mapper" and key == 3:
            raise error
        return left_durations[key]

    def right_mapper(key):
        if origin == "right_mapper":
            raise error
        return right_duration

    def on_group(pair):
        key, window = pair

        def on_error(value):
            received.append((key, value))
            if key in left_durations:
                left_durations[key].on_next(None)

        window.subscribe(on_error=on_error)

    left.pipe(ops.group_join(right, left_mapper, right_mapper)).subscribe(
        on_group, outer_errors.append
    )
    left.on_next(1)
    left.on_next(2)
    if origin == "left":
        left.on_error(error)
    elif origin == "right":
        right.on_error(error)
    elif origin == "left_duration":
        left_durations[1].on_error(error)
    elif origin == "right_duration":
        right.on_next(0)
        right_duration.on_error(error)
    elif origin == "left_mapper":
        left.on_next(3)
    else:
        right.on_next(0)
    assert received == [(1, error), (2, error)] + (
        [(3, error)] if origin == "left_mapper" else []
    )
    assert outer_errors == [error]
    assert not left.observers
    assert not right.observers
