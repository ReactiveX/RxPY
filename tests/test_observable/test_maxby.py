import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestMaxBy(unittest.TestCase):
    def test_maxby_empty(self):
        scheduler = TestScheduler()
        msgs = [
            on_next(150, { "key": 1, "value": 'z' }),
            on_completed(250)
        ]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            def selector(x):
                return x["key"]
            return xs.max_by(selector)

        res = scheduler.start(create=create).messages
        self.assertEqual(2, len(res))
        self.assertEqual(0, len(res[0].value.value))
        assert(res[1].value.kind == 'C' and res[1].time == 250)

    def test_maxby_return(self):
        scheduler = TestScheduler()
        msgs = [
            on_next(150, {
                "key": 1,
                "value": 'z'
            }), on_next(210, {
                "key": 2,
                "value": 'a'
            }), on_completed(250)
        ]
        xs = scheduler.create_hot_observable(msgs)
        def create():
            def selector(x):
                return x["key"]
            return xs.max_by(selector)
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
            on_next(150, {
                "key": 1,
                "value": 'z'
            }), on_next(210, {
                "key": 3,
                "value": 'b'
            }), on_next(220, {
                "key": 4,
                "value": 'c'
            }), on_next(230, {
                "key": 2,
                "value": 'a'
            }), on_completed(250)
        ]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            def selector(x):
                return x["key"]
            return xs.max_by(selector)

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
            on_next(150, {
                "key": 1,
                "value": 'z'
            }),
            on_next(210, {
                "key": 3,
                "value": 'b'
            }),
            on_next(215, {
                "key": 2,
                "value": 'd'
            }),
            on_next(220, {
                "key": 3,
                "value": 'c'
            }),
            on_next(225, {
                "key": 2,
                "value": 'y'
            }),
            on_next(230, {
                "key": 4,
                "value": 'a'
            }),
            on_next(235, {
                "key": 4,
                "value": 'r'
            }),
            on_completed(250)
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
            on_next(150, {
                "key": 1,
                "value": 'z'
            }),
            on_error(210, ex)
        ]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.max_by(lambda x: x["key"])

        res = scheduler.start(create=create).messages

        res.assert_equal(on_error(210, ex))

    def test_maxby_never(self):
        scheduler = TestScheduler()
        msgs = [
            on_next(150, {
                "key": 1,
                "value": 'z'
            })
        ]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.max_by(lambda x: x["key"])

        res = scheduler.start(create=create).messages
        res.assert_equal()

# def test_MaxBy_Comparer_Empty():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }),
#         on_completed(250)
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
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_next(210, {
#             key: 2,
#             value: 'a'
#         }), on_completed(250)
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
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_next(210, {
#             key: 3,
#             value: 'b'
#         }), on_next(220, {
#             key: 4,
#             value: 'c'
#         }), on_next(230, {
#             key: 2,
#             value: 'a'
#         }), on_completed(250)
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
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_error(210, ex)
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
#     res.assert_equal(on_error(210, ex))

# def test_MaxBy_Comparer_Never():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
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
#     res.assert_equal()

# def test_MaxBy_SelectorThrows():
#     var ex, msgs, res, reverseComparer, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_next(210, {
#             key: 3,
#             value: 'b'
#         }), on_next(220, {
#             key: 2,
#             value: 'c'
#         }), on_next(230, {
#             key: 4,
#             value: 'a'
#         }), on_completed(250)
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
#     res.assert_equal(on_error(210, ex))

    def test_maxby_comparerthrows(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [
            on_next(150, {
                "key": 1,
                "value": 'z'
            }), on_next(210, {
                "key": 3,
                "value": 'b'
            }), on_next(220, {
                "key": 2,
                "value": 'c'
            }), on_next(230, {
                "key": 4,
                "value": 'a'
            }), on_completed(250)
        ]
        def reverse_comparer(a, b):
            raise Exception(ex)

        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.max_by(lambda x: x["key"], reverse_comparer)

        res = scheduler.start(create=create).messages
        res.assert_equal(on_error(220, ex))

