import unittest

import rx
from rx.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestCase(unittest.TestCase):
    def test_case_one(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300)
        )
        ys = scheduler.create_hot_observable(
            on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310)
        )
        zs = scheduler.create_hot_observable(
            on_next(230, 21), on_next(240, 22), on_next(290, 23), on_completed(320)
        )
        map = {1: xs, 2: ys}

        def create():
            return rx.case(lambda: 1, map, zs)

        results = scheduler.start(create)

        assert results.messages == [
            on_next(210, 1),
            on_next(240, 2),
            on_next(270, 3),
            on_completed(300),
        ]
        assert xs.subscriptions == [subscribe(200, 300)]
        assert ys.subscriptions == []
        assert zs.subscriptions == []

    def test_case_two(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300)
        )
        ys = scheduler.create_hot_observable(
            on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310)
        )
        zs = scheduler.create_hot_observable(
            on_next(230, 21), on_next(240, 22), on_next(290, 23), on_completed(320)
        )
        map = {1: xs, 2: ys}

        def create():
            return rx.case(lambda: 2, map, zs)

        results = scheduler.start(create)

        assert results.messages == [
            on_next(220, 11),
            on_next(250, 12),
            on_next(280, 13),
            on_completed(310),
        ]
        assert xs.subscriptions == []
        assert ys.subscriptions == [subscribe(200, 310)]
        assert zs.subscriptions == []

    def test_case_three(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300)
        )
        ys = scheduler.create_hot_observable(
            on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310)
        )
        zs = scheduler.create_hot_observable(
            on_next(230, 21), on_next(240, 22), on_next(290, 23), on_completed(320)
        )
        map = {1: xs, 2: ys}

        def create():
            return rx.case(lambda: 3, map, zs)

        results = scheduler.start(create)

        assert results.messages == [
            on_next(230, 21),
            on_next(240, 22),
            on_next(290, 23),
            on_completed(320),
        ]
        assert xs.subscriptions == []
        assert ys.subscriptions == []
        assert zs.subscriptions == [subscribe(200, 320)]

    def test_case_on_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300)
        )
        ys = scheduler.create_hot_observable(
            on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310)
        )
        zs = scheduler.create_hot_observable(
            on_next(230, 21), on_next(240, 22), on_next(290, 23), on_completed(320)
        )
        map = {1: xs, 2: ys}

        def create():
            def mapper():
                raise Exception(ex)

            return rx.case(mapper, map, zs)

        results = scheduler.start(create)

        assert results.messages == [on_error(200, ex)]
        assert xs.subscriptions == []
        assert ys.subscriptions == []
        assert zs.subscriptions == []

    def test_case_with_default_one(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300)
        )
        ys = scheduler.create_hot_observable(
            on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310)
        )
        map = {1: xs, 2: ys}

        def create():
            return rx.case(lambda: 1, map)

        results = scheduler.start(create=create)

        assert results.messages == [
            on_next(210, 1),
            on_next(240, 2),
            on_next(270, 3),
            on_completed(300),
        ]
        assert xs.subscriptions == [subscribe(200, 300)]
        assert ys.subscriptions == []

    def test_case_with_default_two(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300)
        )
        ys = scheduler.create_hot_observable(
            on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310)
        )
        map = {1: xs, 2: ys}

        def create():
            return rx.case(lambda: 2, map)

        results = scheduler.start(create=create)

        assert results.messages == [
            on_next(220, 11),
            on_next(250, 12),
            on_next(280, 13),
            on_completed(310),
        ]
        assert xs.subscriptions == []
        assert ys.subscriptions == [subscribe(200, 310)]

    def test_case_with_default_three(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300)
        )
        ys = scheduler.create_hot_observable(
            on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310)
        )
        map = {1: xs, 2: ys}

        def create():
            return rx.case(lambda: 3, map)

        results = scheduler.start(create=create)

        assert results.messages == [on_completed(200)]
        assert xs.subscriptions == []
        assert ys.subscriptions == []

    def test_case_with_default_on_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300)
        )
        ys = scheduler.create_hot_observable(
            on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310)
        )
        map = {1: xs, 2: ys}

        def create():
            def mapper():
                raise Exception(ex)

            return rx.case(mapper, map)

        results = scheduler.start(create)

        assert results.messages == [on_error(200, ex)]
        assert xs.subscriptions == []
        assert ys.subscriptions == []
