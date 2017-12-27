import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestMaxBy(unittest.TestCase):
    def test_maxby_empty(self):
        scheduler = TestScheduler()
        msgs = [
            send(150, { "key": 1, "value": 'z' }),
            close(250)
        ]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            def mapper(x):
                return x["key"]
            return xs.max_by(mapper)

        res = scheduler.start(create=create).messages
        self.assertEqual(2, len(res))
        self.assertEqual(0, len(res[0].value.value))
        assert(res[1].value.kind == 'C' and res[1].time == 250)

    def test_maxby_return(self):
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
        xs = scheduler.create_hot_observable(msgs)
        def create():
            def mapper(x):
                return x["key"]
            return xs.max_by(mapper)
        res = scheduler.start(create=create).messages
        self.assertEqual(2, len(res))
        assert(res[0].value.kind == 'N')
        self.assertEqual(1, len(res[0].value.value))
        self.assertEqual(2, res[0].value.value[0]["key"])
        self.assertEqual('a', res[0].value.value[0]["value"])
        assert(res[1].value.kind == 'C' and res[1].time == 250)

    def test_maxby_some(self):
        scheduler = TestScheduler()
        msgs = [
            send(150, {
                "key": 1,
                "value": 'z'
            }), send(210, {
                "key": 3,
                "value": 'b'
            }), send(220, {
                "key": 4,
                "value": 'c'
            }), send(230, {
                "key": 2,
                "value": 'a'
            }), close(250)
        ]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            def mapper(x):
                return x["key"]
            return xs.max_by(mapper)

        res = scheduler.start(create=create).messages
        self.assertEqual(2, len(res))
        assert(res[0].value.kind == 'N')
        self.assertEqual(1, len(res[0].value.value[0]["value"]))
        self.assertEqual(4, res[0].value.value[0]["key"])
        self.assertEqual('c', res[0].value.value[0]["value"])
        assert(res[1].value.kind == 'C' and res[1].time == 250)

    def test_maxby_multiple(self):
        scheduler = TestScheduler()
        msgs = [
            send(150, {
                "key": 1,
                "value": 'z'
            }),
            send(210, {
                "key": 3,
                "value": 'b'
            }),
            send(215, {
                "key": 2,
                "value": 'd'
            }),
            send(220, {
                "key": 3,
                "value": 'c'
            }),
            send(225, {
                "key": 2,
                "value": 'y'
            }),
            send(230, {
                "key": 4,
                "value": 'a'
            }),
            send(235, {
                "key": 4,
                "value": 'r'
            }),
            close(250)
        ]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.max_by(lambda x: x["key"])

        res = scheduler.start(create=create).messages

        self.assertEqual(2, len(res))
        assert(res[0].value.kind == 'N')
        self.assertEqual(2, len(res[0].value.value))
        self.assertEqual(4, res[0].value.value[0]["key"])
        self.assertEqual('a', res[0].value.value[0]["value"])
        self.assertEqual(4, res[0].value.value[1]["key"])
        self.assertEqual('r', res[0].value.value[1]["value"])
        assert(res[1].value.kind == 'C' and res[1].time == 250)


    def test_maxby_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [
            send(150, {
                "key": 1,
                "value": 'z'
            }),
            throw(210, ex)
        ]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.max_by(lambda x: x["key"])

        res = scheduler.start(create=create).messages

        assert res == [throw(210, ex)]

    def test_maxby_never(self):
        scheduler = TestScheduler()
        msgs = [
            send(150, {
                "key": 1,
                "value": 'z'
            })
        ]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.max_by(lambda x: x["key"])

        res = scheduler.start(create=create).messages
        assert res == []

# def test_MaxBy_Comparer_Empty():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [
#         send(150, {
#             key: 1,
#             value: 'z'
#         }),
#         close(250)
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a < b) {
#             return 1
#         }
#         return 0
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.max_by(function (x) {
#             return x.key
#         }, reverseComparer)
#     }).messages
#     self.assertEqual(2, res.length)
#     self.assertEqual(0, res[0].value.value.length)
#     assert(res[1].value.kind == 'C' and res[1].time == 250)


# def test_MaxBy_Comparer_Return():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [
#         send(150, {
#             key: 1,
#             value: 'z'
#         }), send(210, {
#             key: 2,
#             value: 'a'
#         }), close(250)
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a < b) {
#             return 1
#         }
#         return 0
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.max_by(function (x) {
#             return x.key
#         }, reverseComparer)
#     }).messages
#     self.assertEqual(2, res.length)
#     assert(res[0].value.kind == 'N')
#     self.assertEqual(1, res[0].value.value.length)
#     self.assertEqual(2, res[0].value.value[0].key)
#     self.assertEqual('a', res[0].value.value[0].value)
#     assert(res[1].value.kind == 'C' and res[1].time == 250)


# def test_MaxBy_Comparer_Some():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [
#         send(150, {
#             key: 1,
#             value: 'z'
#         }), send(210, {
#             key: 3,
#             value: 'b'
#         }), send(220, {
#             key: 4,
#             value: 'c'
#         }), send(230, {
#             key: 2,
#             value: 'a'
#         }), close(250)
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a < b) {
#             return 1
#         }
#         return 0
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.max_by(function (x) {
#             return x.key
#         }, reverseComparer)
#     }).messages
#     self.assertEqual(2, res.length)
#     assert(res[0].value.kind == 'N')
#     self.assertEqual(1, res[0].value.value.length)
#     equal(2, res[0].value.value[0].key)
#     self.assertEqual('a', res[0].value.value[0].value)
#     assert(res[1].value.kind == 'C' and res[1].time == 250)


# def test_MaxBy_Comparer_Throw():
#     var ex, msgs, res, reverseComparer, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [
#         send(150, {
#             key: 1,
#             value: 'z'
#         }), throw(210, ex)
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a < b) {
#             return 1
#         }
#         return 0
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.max_by(function (x) {
#             return x.key
#         }, reverseComparer)
#     }).messages
#     assert res == [throw(210, ex)]

# def test_MaxBy_Comparer_Never():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [
#         send(150, {
#             key: 1,
#             value: 'z'
#         })
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a < b) {
#             return 1
#         }
#         return 0
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.max_by(function (x) {
#             return x.key
#         }, reverseComparer)
#     }).messages
#     assert res == []

# def test_MaxBy_SelectorThrows():
#     var ex, msgs, res, reverseComparer, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [
#         send(150, {
#             key: 1,
#             value: 'z'
#         }), send(210, {
#             key: 3,
#             value: 'b'
#         }), send(220, {
#             key: 2,
#             value: 'c'
#         }), send(230, {
#             key: 4,
#             value: 'a'
#         }), close(250)
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a < b) {
#             return 1
#         }
#         return 0
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.max_by(function (x) {
#             throw ex
#         }, reverseComparer)
#     }).messages
#     assert res == [throw(210, ex)]

    def test_maxby_comparerthrows(self):
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
            raise Exception(ex)

        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.max_by(lambda x: x["key"], reverse_comparer)

        res = scheduler.start(create=create).messages
        assert res == [throw(220, ex)]

