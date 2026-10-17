import pytest

import reactivex
from reactivex import operators as ops
from reactivex.scheduler import ImmediateScheduler
from reactivex.subject import Subject
from reactivex.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_error = ReactiveTest.on_error
on_completed = ReactiveTest.on_completed
subscribe = ReactiveTest.subscribe


@pytest.mark.parametrize(
    "termination",
    ["complete", "source", "key", "element", "subject", "duration", "duration_signal"],
)
def test_group_by_until_terminal_notification_can_expire_groups(termination):
    scheduler = TestScheduler()
    error = RuntimeError("terminal failure")
    source = scheduler.create_hot_observable(
        on_next(210, 1),
        on_next(220, 2),
        on_next(230, 3),
        on_error(240, error) if termination == "source" else on_completed(240),
    )
    groups = []
    subject_count = 0

    def key_mapper(value):
        if termination == "key" and value == 3:
            raise error
        return value

    def element_mapper(value):
        if termination == "element" and value == 3:
            raise error
        return value

    def subject_mapper():
        nonlocal subject_count
        subject_count += 1
        if termination == "subject" and subject_count == 3:
            raise error
        return Subject()

    def duration_mapper(group):
        if termination == "duration" and group.key == 3:
            raise error
        if termination == "duration_signal" and group.key == 1:
            return scheduler.create_hot_observable(on_error(230, error))
        return group.pipe(
            ops.ignore_elements(),
            ops.catch(
                lambda error, source: reactivex.empty(scheduler=ImmediateScheduler())
            ),
        )

    def record_group(group):
        observer = scheduler.create_observer()
        groups.append(observer)
        group.subscribe(observer, scheduler=scheduler)

    results = scheduler.start(
        lambda: source.pipe(
            ops.group_by_until(
                key_mapper, element_mapper, duration_mapper, subject_mapper
            ),
            ops.do_action(record_group),
            ops.ignore_elements(),
        )
    )

    time = 240 if termination in ("complete", "source") else 230
    terminal = (
        on_completed(time) if termination == "complete" else on_error(time, error)
    )
    assert results.messages == [terminal]
    assert groups[0].messages == [on_next(210, 1), terminal]
    assert groups[1].messages == [on_next(220, 2), terminal]
    assert source.subscriptions == [subscribe(200, time)]

    expected_count = 2 if termination in ("key", "subject", "duration") else 3
    assert len(groups) == expected_count
    if expected_count == 3:
        expected = [] if termination == "element" else [on_next(230, 3)]
        assert groups[2].messages == expected + [terminal]
