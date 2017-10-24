from functools import reduce
import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest
from rx.testing.recorded import is_next, is_completed, is_error

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestCatch(unittest.TestCase):

    def _base_catch_exception_test(self, msgs, expected_msgs=None, use_chaining_api=True):
        """Given lists of messages for successive observables, creates the
        appropriate observables and chains them together using catch_exception.
        Tests that the actions seen by a subscriber match the expected
        messages.

        Params:

        :param msgs:
            List of lists of expected messages.
        :param expected_msgs:
            List of expected messages received by subscribers. If not provided,
            a "best guess" is used. Note that this "best guess" currently
            doesn't perform well with non-terminating Observables (i.e.
            Observable.never()).
        :param use_chaining_api:
            Whether to construct the catch_exception call by repeated chaining
            off of instance methods, or by calling Observable.catch_exception
            at the class level.
        """
        scheduler = TestScheduler()

        def _ms_dispatch(ms):
            if ms == []:
                return Observable.never()
            else:
                return scheduler.create_hot_observable(ms)

        os = [_ms_dispatch(ms) for ms in msgs]

        def create():
            if use_chaining_api:
                return reduce(lambda o, catcher: o.catch_exception(catcher), os)
            else:
                return Observable.catch_exception(os)

        if expected_msgs is None:
            all_msgs = reduce(lambda acc, ms: acc + ms, msgs)

            # This is an "imperative specification" of the expected behavior
            # of catch_exception.
            expected_msgs = []
            for msg in all_msgs:
                if is_completed(msg):
                    expected_msgs.append(msg)
                    break
                elif is_error(msg):
                    continue
                elif is_next(msg):
                    expected_msgs.append(msg)

            expected_msgs = expected_msgs[1:]

            # If the final handler throws, catch_exception throws.
            if is_error(all_msgs[-1]):
                expected_msgs.append(all_msgs[-1])

        results = scheduler.start(create)

        results.messages.assert_equal(*expected_msgs)

    def test_catch_no_errors(self):
        msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(230)]
        msgs2 = [on_next(240, 5), on_completed(250)]

        self._base_catch_exception_test([msgs1, msgs2])

    def test_catch_never(self):
        msgs2 = [on_next(240, 5), on_completed(250)]

        # We don't do well with Observable.never(), so we pass expected_msgs.
        self._base_catch_exception_test([[], msgs2], expected_msgs=[])

    def test_catch_empty(self):
        msgs1 = [on_next(150, 1), on_completed(230)]
        msgs2 = [on_next(240, 5), on_completed(250)]

        self._base_catch_exception_test([msgs1, msgs2])

    def test_catch_return(self):
        msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
        msgs2 = [on_next(240, 5), on_completed(250)]

        self._base_catch_exception_test([msgs1, msgs2])

    def test_catch_error(self):
        ex = 'ex'
        msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, ex)]
        msgs2 = [on_next(240, 5), on_completed(250)]

        self._base_catch_exception_test([msgs1, msgs2])

    def test_catch_error_never(self):
        ex = 'ex'
        msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, ex)]

        # We don't do well with Observable.never(), so we pass expected_msgs.
        self._base_catch_exception_test([msgs1, []], expected_msgs=[on_next(210, 2), on_next(220, 3)])

    def test_catch_error_error(self):
        ex = 'ex'
        msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, 'ex1')]
        msgs2 = [on_next(240, 4), on_error(250, ex)]

        self._base_catch_exception_test([msgs1, msgs2])

    def test_catch_multiple(self):
        ex = 'ex'
        msgs1 = [on_next(150, 1), on_next(210, 2), on_error(215, ex)]
        msgs2 = [on_next(220, 3), on_error(225, ex)]
        msgs3 = [on_next(230, 4), on_completed(235)]

        self._base_catch_exception_test([msgs1, msgs2, msgs3], use_chaining_api=False)

    def test_catch_error_specific_caught(self):
        ex = 'ex'
        handler_called = [False]
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, ex)]
        msgs2 = [on_next(240, 4), on_completed(250)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            def handler(e, o):
                handler_called[0] = True
                return o2

            return o1.catch_exception(handler)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(240, 4), on_completed(250))
        assert(handler_called[0])

    def test_catch_error_specific_caught_immediate(self):
        ex = 'ex'
        handler_called = [False]
        scheduler = TestScheduler()
        msgs2 = [on_next(240, 4), on_completed(250)]
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            def handler(e, o):
                handler_called[0] = True
                return o2

            return Observable.throw_exception('ex').catch_exception(handler)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(240, 4), on_completed(250))
        assert(handler_called[0])

    def test_catch_handler_throws(self):
        ex = 'ex'
        ex2 = 'ex2'
        handler_called = [False]
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, ex)]
        o1 = scheduler.create_hot_observable(msgs1)

        def create():
            def handler(e, o):
                handler_called[0] = True
                raise Exception(ex2)
            return o1.catch_exception(handler)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_error(230, ex2))
        assert(handler_called[0])

    def test_catch_nested_outer_catches(self):
        ex = 'ex'
        first_handler_called = [False]
        second_handler_called = [False]
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_error(215, ex)]
        msgs2 = [on_next(220, 3), on_completed(225)]
        msgs3 = [on_next(220, 4), on_completed(225)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)
        o3 = scheduler.create_hot_observable(msgs3)

        def create():
            def handler1(e, o):
                first_handler_called[0] = True
                return o2
            def handler2(e, o):
                second_handler_called[0] = True
                return o3
            return o1.catch_exception(handler1).catch_exception(handler2)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_completed(225))
        assert(first_handler_called[0])
        assert(not second_handler_called[0])

    def test_catch_throw_from_nested_catch(self):
        ex = 'ex'
        ex2 = 'ex'
        first_handler_called = [False]
        second_handler_called = [False]
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_error(215, ex)]
        msgs2 = [on_next(220, 3), on_error(225, ex2)]
        msgs3 = [on_next(230, 4), on_completed(235)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)
        o3 = scheduler.create_hot_observable(msgs3)

        def create():
            def handler1(e, o):
                first_handler_called[0] = True
                assert(e == ex)
                return o2
            def handler2(e, o):
                second_handler_called[0] = True
                assert(e == ex2)
                return o3
            return o1.catch_exception(handler1).catch_exception(handler2)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(235))
        assert(first_handler_called[0])
        assert(second_handler_called[0])
