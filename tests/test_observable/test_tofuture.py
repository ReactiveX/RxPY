
import unittest
import asyncio

import rx
from rx.internal.exceptions import SequenceContainsNoElementsError
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

        self.assertRaises(SequenceContainsNoElementsError, loop.run_until_complete, go())
