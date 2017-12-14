import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass


# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)


class TestMinBy(unittest.TestCase):
    def test_min_by_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, { "key": 1, "value": 'z' }), close(250))

        def create():
            return xs.min_by(lambda x: x["key"])

        res = scheduler.start(create=create).messages
        assert(2 == len(res))
        assert(0 == len(res[0].value.value))
        assert(res[1].value.kind == 'C' and res[1].time == 250)

    def test_min_by_return(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(150, { "key": 1, "value": 'z' }),
            send(210, { "key": 2, "value": 'a' }),
            close(250))

        def create():
            return xs.min_by(lambda x: x["key"])

        res = scheduler.start(create=create).messages
        self.assertEqual(2, len(res))
        assert(res[0].value.kind == 'N')
        self.assertEqual(1, len(res[0].value.value))
        self.assertEqual(2, res[0].value.value[0]["key"])
        self.assertEqual('a', res[0].value.value[0]["value"])
        assert(res[1].value.kind == 'C' and res[1].time == 250)

    def test_min_by_some(self):
        scheduler = TestScheduler()
        msgs = [
            send(150, {
                "key": 1,
                "value": 'z'
            }), send(210, {
                "key": 3,
                "value": 'b'
            }), send(220, {
                "key": 2,
                "value": 'c'
            }), send(230, {
                "key": 4,
                "value": 'a'
            }), close(250)
        ]

        xs = scheduler.create_hot_observable(msgs)
        def create():
            return xs.min_by(lambda x: x["key"])
        res = scheduler.start(create=create).messages

        self.assertEqual(2, len(res))
        assert(res[0].value.kind == 'N')
        self.assertEqual(1, len(res[0].value.value))
        self.assertEqual(2, res[0].value.value[0]["key"])
        self.assertEqual('c', res[0].value.value[0]["value"])
        assert(res[1].value.kind == 'C' and res[1].time == 250)

    def test_min_by_multiple(self):
        scheduler = TestScheduler()
        msgs = [
            send(150, {
                "key": 1,
                "value": 'z'
            }), send(210, {
                "key": 3,
                "value": 'b'
            }), send(215, {
                "key": 2,
                "value": 'd'
            }), send(220, {
                "key": 3,
                "value": 'c'
            }), send(225, {
                "key": 2,
                "value": 'y'
            }), send(230, {
                "key": 4,
                "value": 'a'
            }), send(235, {
                "key": 4,
                "value": 'r'
            }), close(250)
        ]
        xs = scheduler.create_hot_observable(msgs)
        def create():
            return xs.min_by(lambda x: x["key"])
        res = scheduler.start(create=create).messages

        self.assertEqual(2, len(res))
        assert(res[0].value.kind == 'N')
        self.assertEqual(2, len(res[0].value.value))
        self.assertEqual(2, res[0].value.value[0]["key"])
        self.assertEqual('d', res[0].value.value[0]["value"])
        self.assertEqual(2, res[0].value.value[1]["key"])
        self.assertEqual('y', res[0].value.value[1]["value"])
        assert(res[1].value.kind == 'C' and res[1].time == 250)

    def test_min_by_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [
            send(150, {
                "key": 1,
                "value": 'z'
            }), throw(210, ex)
        ]
        xs = scheduler.create_hot_observable(msgs)
        def create():
            return xs.min_by(lambda x: x["key"])
        res = scheduler.start(create=create).messages
        assert res == [throw(210, ex)]

    def test_min_by_never(self):
        scheduler = TestScheduler()
        msgs = [
            send(150, {
                "key": 1,
                "value": 'z'
            })
        ]
        xs = scheduler.create_hot_observable(msgs)
        def create():
            return xs.min_by(lambda x: x["key"])
        res = scheduler.start(create=create).messages

        assert res == []

    def test_min_by_comparer_empty(self):
        scheduler = TestScheduler()
        msgs = [
            send(150, {
                "key": 1,
                "value": 'z'
            }), close(250)
        ]
        def reverse_comparer(a, b):
            if a > b:
                return -1

            if a == b:
                return 0
            return 1

        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.min_by(lambda x: x["key"], reverse_comparer)

        res = scheduler.start(create=create).messages
        self.assertEqual(2, len(res))
        self.assertEqual(0, len(res[0].value.value))
        assert(res[1].value.kind == 'C' and res[1].time == 250)

    def test_min_by_comparer_return(self):
        scheduler = TestScheduler()
        msgs = [
            send(150, {
                "key": 1,
                "value": 'z'
            }), send(210, {
                "key": 2,
                "value": 'a'
            }), close(250)
        ]
        def reverse_comparer(a, b):
            if a > b:
                return -1

            if a == b:
                return 0
            return 1

        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.min_by(lambda x: x["key"], reverse_comparer)

        res = scheduler.start(create=create).messages
        self.assertEqual(2, len(res))
        assert(res[0].value.kind == 'N')
        self.assertEqual(1, len(res[0].value.value))
        self.assertEqual(2, res[0].value.value[0]["key"])
        self.assertEqual('a', res[0].value.value[0]["value"])
        assert(res[1].value.kind == 'C' and res[1].time == 250)

    def test_min_by_comparer_some(self):
        scheduler = TestScheduler()
        msgs = [
            send(150, {
                "key": 1,
                "value": 'z'
            }), send(210, {
                "key": 3,
                "value": 'b'
            }), send(220, {
                "key": 20,
                "value": 'c'
            }), send(230, {
                "key": 4,
                "value": 'a'
            }), close(250)
        ]
        def reverse_comparer(a, b):
            if a > b:
                return -1

            if a == b:
                return 0
            return 1

        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.min_by(lambda x: x["key"], reverse_comparer)

        res = scheduler.start(create=create).messages
        self.assertEqual(2, len(res))
        assert(res[0].value.kind == 'N')
        self.assertEqual(1, len(res[0].value.value))
        self.assertEqual(20, res[0].value.value[0]["key"])
        self.assertEqual('c', res[0].value.value[0]["value"])
        assert(res[1].value.kind == 'C' and res[1].time == 250)

    def test_min_by_comparer_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [
            send(150, {
                "key": 1,
                "value": 'z'
            }), throw(210, ex)
        ]
        def reverse_comparer(a, b):
            if a > b:
                return -1

            if a == b:
                return 0

            return 1
        def create():
            return xs.min_by(lambda x: x["key"], reverse_comparer)

        xs = scheduler.create_hot_observable(msgs)
        res = scheduler.start(create=create).messages
        assert res == [throw(210, ex)]

    def test_min_by_comparer_never(self):
        scheduler = TestScheduler()
        msgs = [
            send(150, {
                "key": 1,
                "value": 'z'
            })
        ]
        def reverse_comparer(a, b):
            if a > b:
                return -1

            if a == b:
                return 0

            return 1

        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.min_by(lambda x: x["key"], reverse_comparer)

        res = scheduler.start(create=create).messages
        assert res == []

    def test_min_by_selector_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [
            send(150, {
                "key": 1,
                "value": 'z'
            }), send(210, {
                "key": 3,
                "value": 'b'
            }), send(220, {
                "key": 2,
                "value": 'c'
            }), send(230, {
                "key": 4,
                "value": 'a'
            }), close(250)
        ]
        def reverse_comparer(a, b):
            if a > b:
                return -1

            if a == b:
                return 0

            return 1

        xs = scheduler.create_hot_observable(msgs)

        def create():
           return xs.min_by(lambda x: _raise(ex), reverse_comparer)

        res = scheduler.start(create=create).messages
        assert res == [throw(210, ex)]

    def test_min_by_comparer_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [
            send(150, {
                "key": 1,
                "value": 'z'
            }), send(210, {
                "key": 3,
                "value": 'b'
            }), send(220, {
                "key": 2,
                "value": 'c'
            }), send(230, {
                "key": 4,
                "value": 'a'
            }), close(250)
        ]
        def reverse_comparer(a, b):
            _raise(ex)

        xs = scheduler.create_hot_observable(msgs)

        def create():
           return xs.min_by(lambda x: x["key"], reverse_comparer)

        res = scheduler.start(create=create).messages
        assert res == [throw(220, ex)]
