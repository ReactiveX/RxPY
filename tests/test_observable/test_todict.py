import unittest

import rx
from rx import operators as ops
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestToDict(unittest.TestCase):

    def test_to_dict_completed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(110, 1),
            on_next(220, 2),
            on_next(330, 3),
            on_next(440, 4),
            on_next(550, 5),
            on_completed(660)
        )

        def create():
            return xs.pipe(ops.to_dict(lambda x: x * 2, lambda x: x * 4))

        res = scheduler.start(create)
        assert res.messages == [
            on_next(660, {4: 8, 6: 12, 8: 16, 10: 20}),
            on_completed(660)]

        assert xs.subscriptions == [
            subscribe(200, 660)]

    def test_to_dict_error(self):
        scheduler = TestScheduler()

        ex = Exception()

        xs = scheduler.create_hot_observable(
            on_next(110, 1),
            on_next(220, 2),
            on_next(330, 3),
            on_next(440, 4),
            on_next(550, 5),
            on_error(660, ex)
        )

        def create():
            return xs.pipe(ops.to_dict(lambda x: x * 2, lambda x: x * 4))

        res = scheduler.start(create)

        assert res.messages == [
            on_error(660, ex)]

        assert xs.subscriptions == [
           subscribe(200, 660)]


    def test_to_dict_keymapperthrows(self):
        scheduler = TestScheduler()

        ex = Exception()

        xs = scheduler.create_hot_observable(
            on_next(110, 1),
            on_next(220, 2),
            on_next(330, 3),
            on_next(440, 4),
            on_next(550, 5),
            on_completed(600)
          )

        def create():
            def key_mapper(x):
                if x < 4:
                    return x * 2
                else:
                    raise ex
            return xs.pipe(ops.to_dict(key_mapper, lambda x: x * 4))

        res = scheduler.start(create)

        assert res.messages == [
            on_error(440, ex)]

        assert xs.subscriptions == [
            subscribe(200, 440)]

    def test_to_dict_elementmapperthrows(self):
        scheduler = TestScheduler()

        ex = Exception()

        xs = scheduler.create_hot_observable(
            on_next(110, 1),
            on_next(220, 2),
            on_next(330, 3),
            on_next(440, 4),
            on_next(550, 5),
            on_completed(600)
        )

        def value_mapper(x):
            if x < 4:
                return x * 4
            else:
                raise ex

        def create():
            return xs.pipe(ops.to_dict(lambda x: x * 2 , value_mapper))

        res = scheduler.start(create)

        assert res.messages == [
            on_error(440, ex)]

        assert xs.subscriptions == [
            subscribe(200, 440)]

    def test_to_dict_disposed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(110, 1),
            on_next(220, 2),
            on_next(330, 3),
            on_next(440, 4),
            on_next(550, 5)
        )

        def create():
            return xs.pipe(ops.to_dict(lambda x: x * 2, lambda x: x * 4))

        res = scheduler.start(create)

        assert res.messages == []

        assert xs.subscriptions == [
            subscribe(200, 1000)]
