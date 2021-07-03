import unittest

import asyncio
import threading
from datetime import datetime, timedelta

from rx.scheduler.eventloop import AsyncIOThreadSafeScheduler


class TestAsyncIOThreadSafeScheduler(unittest.TestCase):

    def test_asyncio_threadsafe_schedule_now(self):
        loop = asyncio.get_event_loop()
        scheduler = AsyncIOThreadSafeScheduler(loop)
        diff = scheduler.now - datetime.utcfromtimestamp(loop.time())
        assert abs(diff) < timedelta(milliseconds=1)

    def test_asyncio_threadsafe_schedule_now_units(self):
        loop = asyncio.get_event_loop()
        scheduler = AsyncIOThreadSafeScheduler(loop)
        diff = scheduler.now
        yield from asyncio.sleep(0.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    def test_asyncio_threadsafe_schedule_action(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def go():
            scheduler = AsyncIOThreadSafeScheduler(loop)
            ran = False

            def action(scheduler, state):
                nonlocal ran
                ran = True

            def schedule():
                scheduler.schedule(action)

            threading.Thread(target=schedule).start()

            yield from asyncio.sleep(0.1)
            assert ran is True

        loop.run_until_complete(go())

    def test_asyncio_threadsafe_schedule_action_due(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def go():
            scheduler = AsyncIOThreadSafeScheduler(loop)
            starttime = loop.time()
            endtime = None

            def action(scheduler, state):
                nonlocal endtime
                endtime = loop.time()

            def schedule():
                scheduler.schedule_relative(0.2, action)

            threading.Thread(target=schedule).start()

            yield from asyncio.sleep(0.3)
            assert endtime is not None
            diff = endtime - starttime
            assert diff > 0.18

        loop.run_until_complete(go())

    def test_asyncio_threadsafe_schedule_action_cancel(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def go():
            ran = False
            scheduler = AsyncIOThreadSafeScheduler(loop)

            def action(scheduler, state):
                nonlocal ran
                ran = True

            def schedule():
                d = scheduler.schedule_relative(0.05, action)
                d.dispose()

            threading.Thread(target=schedule).start()

            yield from asyncio.sleep(0.3)
            assert ran is False

        loop.run_until_complete(go())

    def cancel_same_thread_common(self, test_body):
        update_state = {
            'ran': False,
            'dispose_completed': False
        }

        def action(scheduler, state):
            update_state['ran'] = True

        # Make the actual test body run in deamon thread, so that in case of
        # failure it doesn't hang indefinitely.
        def thread_target():
            loop = asyncio.new_event_loop()
            scheduler = AsyncIOThreadSafeScheduler(loop)

            test_body(scheduler, action, update_state)

            @asyncio.coroutine
            def go():
                yield from asyncio.sleep(0.2)

            loop.run_until_complete(go())

        thread = threading.Thread(target=thread_target)
        thread.daemon = True
        thread.start()
        thread.join(0.3)
        assert update_state['dispose_completed'] is True
        assert update_state['ran'] is False


    def test_asyncio_threadsafe_cancel_non_relative_same_thread(self):
        def test_body(scheduler, action, update_state):
            d = scheduler.schedule(action)

            # Test case when dispose is called on thread on which loop is not
            # yet running, and non-relative schedele is used.
            d.dispose()
            update_state['dispose_completed'] = True

        self.cancel_same_thread_common(test_body)


    def test_asyncio_threadsafe_schedule_action_cancel_same_thread(self):
        def test_body(scheduler, action, update_state):
            d = scheduler.schedule_relative(0.05, action)

            # Test case when dispose is called on thread on which loop is not
            # yet running, and relative schedule is used.
            d.dispose()
            update_state['dispose_completed'] = True

        self.cancel_same_thread_common(test_body)


    def test_asyncio_threadsafe_schedule_action_cancel_same_loop(self):
        def test_body(scheduler, action, update_state):
            d = scheduler.schedule_relative(0.1, action)

            def do_dispose():
                d.dispose()
                update_state['dispose_completed'] = True

            # Test case when dispose is called in loop's callback.
            scheduler._loop.call_soon(do_dispose)

        self.cancel_same_thread_common(test_body)
