import asyncio
import unittest

import rx
import rx.operators as ops
from rx.internal.exceptions import SequenceContainsNoElementsError
from rx.subject import Subject
from rx.testing import ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestToFuture(unittest.TestCase):
    def test_await_success(self):
        loop = asyncio.get_event_loop()
        result = None

        async def go():
            nonlocal result
            source = rx.return_value(42)
            result = await source

        loop.run_until_complete(go())
        assert result == 42

    def test_await_success_on_sequence(self):
        loop = asyncio.get_event_loop()
        result = None

        async def go():
            nonlocal result
            source = rx.from_([40, 41, 42])
            result = await source

        loop.run_until_complete(go())
        assert result == 42

    def test_await_error(self):
        loop = asyncio.get_event_loop()
        error = Exception("error")
        result = None

        async def go():
            nonlocal result
            source = rx.throw(error)
            try:
                result = await source
            except Exception as ex:
                result = ex

        loop.run_until_complete(go())
        assert result == error

    def test_await_empty_observable(self):
        loop = asyncio.get_event_loop()
        result = None

        async def go():
            nonlocal result
            source = rx.empty()
            result = await source

        self.assertRaises(
            SequenceContainsNoElementsError, loop.run_until_complete, go()
        )

    def test_await_with_delay(self):
        loop = asyncio.get_event_loop()
        result = None

        async def go():
            nonlocal result
            source = rx.return_value(42).pipe(ops.delay(0.1))
            result = await source

        loop.run_until_complete(go())
        assert result == 42

    def test_cancel(self):
        loop = asyncio.get_event_loop()

        async def go():
            source = rx.return_value(42)
            fut = next(source.__await__())
            # This used to raise an InvalidStateError before we got
            # support for cancellation.
            fut.cancel()
            await fut

        self.assertRaises(asyncio.CancelledError, loop.run_until_complete, go())

    def test_dispose_on_cancel(self):
        loop = asyncio.get_event_loop()
        sub = Subject()

        async def using_sub():
            # Since the subject never completes, this await statement
            # will never be complete either. We wait forever.
            await rx.using(lambda: sub, lambda s: s)

        async def go():
            await asyncio.wait_for(using_sub(), 0.1)

        self.assertRaises(asyncio.TimeoutError, loop.run_until_complete, go())
        # When we cancel the future (due to the time-out), the future
        # automatically disposes the underlying subject.
        self.assertTrue(sub.is_disposed)
