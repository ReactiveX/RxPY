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

    def _base_catch_exception_test(self, msgs, expected_msgs=None, mk_handler=None, use_chaining_api=True):
        """Given lists of messages for successive observables, creates the
        appropriate observables and chains them together using catch_exception.
        Tests that the actions seen by a subscriber match the expected
        messages.

        Params:

        :param msgs:
            List of lists of expected messages. If an element is an Observable, then
            it will be used as-is.
        :param expected_msgs:
            List of expected messages received by subscribers. If not provided,
            a "best guess" is used. Note that this "best guess" currently
            doesn't perform well with non-terminating Observables (i.e.
            Observable.never()). If a test is tricky, provide this manually.
        :param mk_handler:
            ``mk_handler`` should be a higher-order function with type

                handler: (Observable) -> (Observable) -> Observable

            that is, it takes the next observable (defined by ``msgs``) and returns a
            function that can be used as a handler by ``catch_exception``.

            Only used if ``use_chaining_api`` is ``True``.
        :param use_chaining_api:
            Whether to construct the catch_exception call by repeated chaining
            off of instance methods, or by calling Observable.catch_exception
            at the class level.

            If ``False``, then ``mk_handler`` is unused, as the classmethod
            ``Observable.catch_exception`` does not take handlers, only
            Observables.
        """
        scheduler = TestScheduler()


        if mk_handler is None:
            # So ``catch_exception(handler)`` is the same as ``catch_exception(o2)``.
            def mk_handler(o2):
                def handler(e, o1):
                    return o2
                return handler

        def _ms_dispatch(ms):
            if ms == []:
                return Observable.never()
            elif isinstance(ms, Observable):
                return ms
            else:
                return scheduler.create_hot_observable(ms)

        os = [_ms_dispatch(ms) for ms in msgs]

        def create():
            if use_chaining_api:
                return reduce(lambda o, catcher: o.catch_exception(mk_handler(catcher)), os)
            else:
                # Note that you can't use handlers with the classmethod ``catch_exception``.
                return Observable.catch_exception(os)

        if expected_msgs is None:
            # Account for cases in which not all ms in msgs are lists of messages.
            all_msgs = reduce(
                    lambda acc, ms: acc + ms if isinstance(ms, list) else acc,
                    msgs,
                    [],
                    )

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

    def _mk_call_tracked_handler(self, handler):
        """Makes a handler-builder that tracks total calls to the built handler
        across an Observable chain.

        :param handler:
            Function which takes the next Observable, the Exception raised, and
            the source Observable and returns an Observable (or throws).
        """
        # We use the same "counter" for all handlers, so this will count
        # the calls to "all" handlers in a given Observable chain.
        handler_calls = [0]

        def mk_handler(o2):
            def _handler(e, o1):
                handler_calls[0] += 1
                return handler(o2, e, o1)
            return _handler

        return handler_calls, mk_handler

    def _base_call_tracked_handler_test(self, msgs, handler=None, expected_handler_call_count=None, **kwargs):
        if handler is None:
            def handler(o2, e, o1):
                return o2

        handler_calls, mk_handler = self._mk_call_tracked_handler(handler)

        if expected_handler_call_count is None:
            # If ``msgs`` is a generator, this test will not work as intended, as we consume
            # ``msgs`` here.
            expected_handler_call_count = len(msgs) - 1

        self._base_catch_exception_test(msgs, mk_handler=mk_handler, **kwargs)
        assert(handler_calls[0] == expected_handler_call_count)

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

        msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, ex)]
        msgs2 = [on_next(240, 4), on_completed(250)]

        self._base_call_tracked_handler_test([msgs1, msgs2])

    def test_catch_error_specific_caught_immediate(self):
        ex = 'ex'

        msgs2 = [on_next(240, 4), on_completed(250)]

        self._base_call_tracked_handler_test(
                [Observable.throw_exception(ex), msgs2],
                expected_msgs=msgs2,
                )

    def test_catch_handler_throws(self):
        ex = 'ex'

        msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, ex)]

        def handler(o2, e, o1):
            # Note that ``e`` is not an Exception, it's a str, as written.
            raise Exception(e)

        self._base_call_tracked_handler_test([msgs1, []], handler=handler, expected_msgs=msgs1[1:])

    def test_catch_nested_outer_catches(self):
        ex = 'ex'

        msgs1 = [on_next(150, 1), on_next(210, 2), on_error(215, ex)]
        msgs2 = [on_next(220, 3), on_completed(225)]
        msgs3 = [on_next(220, 4), on_completed(225)]

        # Since we complete in the first handler, we should only call one handler.
        self._base_call_tracked_handler_test([msgs1, msgs2, msgs3], expected_handler_call_count=1)

    def test_catch_throw_from_nested_catch(self):
        ex = 'ex'
        ex2 = 'ex'

        msgs1 = [on_next(150, 1), on_next(210, 2), on_error(215, ex)]
        msgs2 = [on_next(220, 3), on_error(225, ex2)]
        msgs3 = [on_next(230, 4), on_completed(235)]

        self._base_call_tracked_handler_test([msgs1, msgs2, msgs3])
