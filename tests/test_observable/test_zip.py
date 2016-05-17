import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestZip(unittest.TestCase):

    def test_zip_never_never(self):
        scheduler = TestScheduler()
        o1 = Observable.never()
        o2 = Observable.never()

        def create():
            return o1.zip(o2, lambda x, y: x + y)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_zip_never_empty(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_completed(210)]
        o1 = Observable.never()
        o2 = scheduler.create_hot_observable(msgs)

        def create():
            return o1.zip(o2, lambda x, y: x + y)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_zip_empty_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(210)]
        msgs2 = [on_next(150, 1), on_completed(210)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        results.messages.assert_equal(on_completed(210))

    def test_zip_empty_non_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(210)]
        msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        results.messages.assert_equal(on_completed(215))

    def test_zip_non_empty_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(210)]
        msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.zip(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        results.messages.assert_equal(on_completed(215))

    def test_zip_never_non_empty(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(215, 2), on_completed(220)]
        e1 = scheduler.create_hot_observable(msgs)
        e2 = Observable.never()

        def create():
            return e2.zip(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_zip_non_empty_never(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(215, 2), on_completed(220)]
        e1 = scheduler.create_hot_observable(msgs)
        e2 = Observable.never()

        def create():
            return e1.zip(e2, lambda x, y: x + y)
        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_zip_non_empty_non_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
        msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(240)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(220, 2 + 3), on_completed(240))

    def test_zip_empty_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(230)]
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(220, ex))

    def test_zip_error_empty(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(230)]
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.zip(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(220, ex))

    def test_zip_never_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = Observable.never()
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(220, ex))

    def test_zip_error_never(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = Observable.never()
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.zip(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(220, ex))

    def test_zip_error_error(self):
        ex1 = 'ex1'
        ex2 = 'ex2'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_error(230, ex1)]
        msgs2 = [on_next(150, 1), on_error(220, ex2)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.zip(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(220, ex2))

    def test_zip_some_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(220, ex))

    def test_zip_error_some(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
        msgs2 = [on_next(150, 1), on_error(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.zip(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(220, ex))

    def test_zip_some_data_asymmetric1(self):
        scheduler = TestScheduler()

        def msgs1_factory():
            results = []
            for i in range(5):
                results.append(on_next(205 + i * 5, i))
            return results
        msgs1 = msgs1_factory()

        def msgs2_factory():
            results = []
            for i in range(10):
                results.append(on_next(205 + i * 8, i))
            return results
        msgs2 = msgs2_factory()

        length = min(len(msgs1), len(msgs2))
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, lambda x, y: x + y)

        results = scheduler.start(create).messages
        assert(length == len(results))
        for i in range(length):
            _sum = msgs1[i].value.value + msgs2[i].value.value
            time = max(msgs1[i].time, msgs2[i].time)
            assert(results[i].value.kind == 'N' and results[i].time == time and results[i].value.value == _sum)

    def test_zip_some_data_asymmetric2(self):
        scheduler = TestScheduler()
        def msgs1_factory():
            results = []
            for i in range(10):
                results.append(on_next(205 + i * 5, i))

            return results
        msgs1 = msgs1_factory()

        def msgs2_factory():
            results = []
            for i in range(5):
                results.append(on_next(205 + i * 8, i))
            return results
        msgs2 = msgs2_factory()

        length = min(len(msgs1), len(msgs2))
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, lambda x, y: x + y)

        results = scheduler.start(create).messages
        assert(length == len(results))
        for i in range(length):
            _sum = msgs1[i].value.value + msgs2[i].value.value
            time = max(msgs1[i].time, msgs2[i].time)
            assert(results[i].value.kind == 'N' and results[i].time == time and results[i].value.value == _sum)

    def test_zip_some_data_symmetric(self):
        scheduler = TestScheduler()
        def msgs1_factory():
            results = []
            for i in range(10):
                results.append(on_next(205 + i * 5, i))
            return results
        msgs1 = msgs1_factory()

        def msgs2_factory():
            results = []
            for i in range(10):
                results.append(on_next(205 + i * 8, i))
            return results
        msgs2 = msgs2_factory()

        length = min(len(msgs1), len(msgs2))
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, lambda x, y: x + y)

        results = scheduler.start(create).messages
        assert(length == len(results))
        for i in range(length):
            _sum = msgs1[i].value.value + msgs2[i].value.value
            time = max(msgs1[i].time, msgs2[i].time)
            assert(results[i].value.kind == 'N' and results[i].time == time and results[i].value.value == _sum)

    def test_zip_selector_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(215, 2), on_next(225, 4), on_completed(240)]
        msgs2 = [on_next(150, 1), on_next(220, 3), on_next(230, 5), on_completed(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            def selector(x, y):
                if y == 5:
                    raise Exception(ex)
                else:
                    return x + y

            return e1.zip(e2, selector)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(220, 2 + 3), on_error(230, ex))

    def test_zip_with_enumerable_never_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(on_next(150, 1))
        n2 = []

        def create():
            def selector(x, y):
                return x + y
            return n1.zip(n2, selector)

        results = scheduler.start(create)

        results.messages.assert_equal()
        n1.subscriptions.assert_equal(subscribe(200, 1000))

    def test_zip_with_enumerable_empty_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(on_next(150, 1), on_completed(210))
        n2 = []

        def create():
            def selector(x,y):
                return x + y
            return n1.zip(n2, selector)

        results = scheduler.start(create)

        results.messages.assert_equal(on_completed(210))
        n1.subscriptions.assert_equal(subscribe(200, 210))

    def test_zip_with_enumerable_empty_non_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(on_next(150, 1), on_completed(210))
        n2 = [2]

        def create():
            def selector(x,y):
                return x + y
            return n1.zip(n2, selector)

        results = scheduler.start(create)

        results.messages.assert_equal(on_completed(210))
        n1.subscriptions.assert_equal(subscribe(200, 210))

    def test_zip_with_enumerable_non_empty_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(on_next(150, 1), on_next(215, 2), on_completed(220))
        n2 = []

        def create():
            def selector(x, y):
                return x + y
            return n1.zip(n2, selector)
        results = scheduler.start(create)

        results.messages.assert_equal(on_completed(215))
        n1.subscriptions.assert_equal(subscribe(200, 215))

    def test_zip_with_enumerable_never_non_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(on_next(150, 1))
        n2 = [2]

        def create():
            def selector(x, y):
                return x + y
            return n1.zip(n2, selector)

        results = scheduler.start(create)

        results.messages.assert_equal()
        n1.subscriptions.assert_equal(subscribe(200, 1000))

    def test_zip_with_enumerable_non_empty_non_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(on_next(150, 1), on_next(215, 2), on_completed(230))
        n2 = [3]

        def create():
            def selector(x, y):
                return x + y
            return n1.zip(n2, selector)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(215, 2 + 3), on_completed(230))
        n1.subscriptions.assert_equal(subscribe(200, 230))

    def test_zip_with_enumerable_error_empty(self):
        ex = 'ex'
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(on_next(150, 1), on_error(220, ex))
        n2 = []

        def create():
            def selector(x, y):
                return x + y
            return n1.zip(n2, selector)
        results = scheduler.start(create)

        results.messages.assert_equal(on_error(220, ex))
        n1.subscriptions.assert_equal(subscribe(200, 220))

    def test_zip_with_enumerable_error_some(self):
        ex = 'ex'
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(on_next(150, 1), on_error(220, ex))
        n2 = [2]

        def create():
            def selector(x, y):
                return x + y
            return n1.zip(n2, selector)
        results = scheduler.start(create)

        results.messages.assert_equal(on_error(220, ex))
        n1.subscriptions.assert_equal(subscribe(200, 220))

    def test_zip_with_enumerable_some_data_both_sides(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5))
        n2 = [5, 4, 3, 2]

        def create():
            def selector(x, y):
                return x + y
            return n1.zip(n2, selector)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, 7), on_next(220, 7), on_next(230, 7), on_next(240, 7))
        n1.subscriptions.assert_equal(subscribe(200, 1000))

    def test_zip_with_enumerable_selectorthrows(self):
        ex = 'ex'
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(on_next(150, 1), on_next(215, 2), on_next(225, 4), on_completed(240))
        n2 = [3, 5]

        def create():
            def selector(x, y):
                if y == 5:
                    raise Exception(ex)
                return x + y
            return n1.zip(n2, selector)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(215, 2 + 3), on_error(225, ex))
        n1.subscriptions.assert_equal(subscribe(200, 225))

