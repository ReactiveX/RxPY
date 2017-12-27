import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
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
            return o1.zip(o2, result_mapper=lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == []

    def test_zip_never_empty(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), close(210)]
        o1 = Observable.never()
        o2 = scheduler.create_hot_observable(msgs)

        def create():
            return o1.zip(o2, result_mapper=lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == []

    def test_zip_empty_empty(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(210)]
        msgs2 = [send(150, 1), close(210)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, result_mapper=lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [close(210)]

    def test_zip_empty_non_empty(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(210)]
        msgs2 = [send(150, 1), send(215, 2), close(220)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, result_mapper=lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [close(215)]

    def test_zip_non_empty_empty(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(210)]
        msgs2 = [send(150, 1), send(215, 2), close(220)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.zip(e1, result_mapper=lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [close(215)]

    def test_zip_never_non_empty(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(215, 2), close(220)]
        e1 = scheduler.create_hot_observable(msgs)
        e2 = Observable.never()

        def create():
            return e2.zip(e1, result_mapper=lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == []

    def test_zip_non_empty_never(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(215, 2), close(220)]
        e1 = scheduler.create_hot_observable(msgs)
        e2 = Observable.never()

        def create():
            return e1.zip(e2, result_mapper=lambda x, y: x + y)
        results = scheduler.start(create)
        assert results.messages == []

    def test_zip_non_empty_non_empty(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), close(230)]
        msgs2 = [send(150, 1), send(220, 3), close(240)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, result_mapper=lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [send(220, 2 + 3), close(240)]

    def test_zip_empty_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(230)]
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, result_mapper=lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_zip_error_empty(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(230)]
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.zip(e1, result_mapper=lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_zip_never_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = Observable.never()
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, result_mapper=lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_zip_error_never(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = Observable.never()
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.zip(e1, result_mapper=lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_zip_error_error(self):
        ex1 = 'ex1'
        ex2 = 'ex2'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), throw(230, ex1)]
        msgs2 = [send(150, 1), throw(220, ex2)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.zip(e1, result_mapper=lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex2)]

    def test_zip_some_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), close(230)]
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, result_mapper=lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_zip_error_some(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), close(230)]
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.zip(e1, result_mapper=lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_zip_some_data_asymmetric1(self):
        scheduler = TestScheduler()

        def msgs1_factory():
            results = []
            for i in range(5):
                results.append(send(205 + i * 5, i))
            return results
        msgs1 = msgs1_factory()

        def msgs2_factory():
            results = []
            for i in range(10):
                results.append(send(205 + i * 8, i))
            return results
        msgs2 = msgs2_factory()

        length = min(len(msgs1), len(msgs2))
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, result_mapper=lambda x, y: x + y)

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
                results.append(send(205 + i * 5, i))

            return results
        msgs1 = msgs1_factory()

        def msgs2_factory():
            results = []
            for i in range(5):
                results.append(send(205 + i * 8, i))
            return results
        msgs2 = msgs2_factory()

        length = min(len(msgs1), len(msgs2))
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, result_mapper=lambda x, y: x + y)

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
                results.append(send(205 + i * 5, i))
            return results
        msgs1 = msgs1_factory()

        def msgs2_factory():
            results = []
            for i in range(10):
                results.append(send(205 + i * 8, i))
            return results
        msgs2 = msgs2_factory()

        length = min(len(msgs1), len(msgs2))
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.zip(e2, result_mapper=lambda x, y: x + y)

        results = scheduler.start(create).messages
        assert(length == len(results))
        for i in range(length):
            _sum = msgs1[i].value.value + msgs2[i].value.value
            time = max(msgs1[i].time, msgs2[i].time)
            assert(results[i].value.kind == 'N' and results[i].time == time and results[i].value.value == _sum)

    def test_zip_mapper_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), send(225, 4), close(240)]
        msgs2 = [send(150, 1), send(220, 3), send(230, 5), close(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            def mapper(x, y):
                if y == 5:
                    raise Exception(ex)
                else:
                    return x + y

            return e1.zip(e2, result_mapper=mapper)

        results = scheduler.start(create)
        assert results.messages == [send(220, 2 + 3), throw(230, ex)]

    def test_zip_with_iterable_never_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(send(150, 1))
        n2 = []

        def create():
            def mapper(x, y):
                return x + y
            return n1.zip(n2, result_mapper=mapper)

        results = scheduler.start(create)

        assert results.messages == []
        assert n1.subscriptions == [subscribe(200, 1000)]

    def test_zip_with_iterable_empty_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(send(150, 1), close(210))
        n2 = []

        def create():
            def mapper(x,y):
                return x + y
            return n1.zip(n2, result_mapper=mapper)

        results = scheduler.start(create)

        assert results.messages == [close(210)]
        assert n1.subscriptions == [subscribe(200, 210)]

    def test_zip_with_iterable_empty_non_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(send(150, 1), close(210))
        n2 = [2]

        def create():
            def mapper(x,y):
                return x + y
            return n1.zip(n2, result_mapper=mapper)

        results = scheduler.start(create)

        assert results.messages == [close(210)]
        assert n1.subscriptions == [subscribe(200, 210)]

    def test_zip_with_iterable_non_empty_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(send(150, 1), send(215, 2), close(220))
        n2 = []

        def create():
            def mapper(x, y):
                return x + y
            return n1.zip(n2, result_mapper=mapper)
        results = scheduler.start(create)

        assert results.messages == [close(215)]
        assert n1.subscriptions == [subscribe(200, 215)]

    def test_zip_with_iterable_never_non_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(send(150, 1))
        n2 = [2]

        def create():
            def mapper(x, y):
                return x + y
            return n1.zip(n2, result_mapper=mapper)

        results = scheduler.start(create)

        assert results.messages == []
        assert n1.subscriptions == [subscribe(200, 1000)]

    def test_zip_with_iterable_non_empty_non_empty(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(send(150, 1), send(215, 2), close(230))
        n2 = [3]

        def create():
            def mapper(x, y):
                return x + y
            return n1.zip(n2, result_mapper=mapper)
        results = scheduler.start(create)

        assert results.messages == [send(215, 2 + 3), close(230)]
        assert n1.subscriptions == [subscribe(200, 230)]

    def test_zip_with_iterable_error_empty(self):
        ex = 'ex'
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(send(150, 1), throw(220, ex))
        n2 = []

        def create():
            def mapper(x, y):
                return x + y
            return n1.zip(n2, result_mapper=mapper)
        results = scheduler.start(create)

        assert results.messages == [throw(220, ex)]
        assert n1.subscriptions == [subscribe(200, 220)]

    def test_zip_with_iterable_error_some(self):
        ex = 'ex'
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(send(150, 1), throw(220, ex))
        n2 = [2]

        def create():
            def mapper(x, y):
                return x + y
            return n1.zip(n2, result_mapper=mapper)
        results = scheduler.start(create)

        assert results.messages == [throw(220, ex)]
        assert n1.subscriptions == [subscribe(200, 220)]

    def test_zip_with_iterable_some_data_both_sides(self):
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 3), send(230, 4), send(240, 5))
        n2 = [5, 4, 3, 2]

        def create():
            def mapper(x, y):
                return x + y
            return n1.zip(n2, result_mapper=mapper)
        results = scheduler.start(create)

        assert results.messages == [send(210, 7), send(220, 7), send(230, 7), send(240, 7)]
        assert n1.subscriptions == [subscribe(200, 1000)]

    def test_zip_with_iterable_mapperthrows(self):
        ex = 'ex'
        scheduler = TestScheduler()
        n1 = scheduler.create_hot_observable(send(150, 1), send(215, 2), send(225, 4), close(240))
        n2 = [3, 5]

        def create():
            def mapper(x, y):
                if y == 5:
                    raise Exception(ex)
                return x + y
            return n1.zip(n2, result_mapper=mapper)
        results = scheduler.start(create)

        assert results.messages == [send(215, 2 + 3), throw(225, ex)]
        assert n1.subscriptions == [subscribe(200, 225)]

