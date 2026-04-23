import asyncio
import os
import threading
import unittest
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from reactivex import abc
from reactivex.scheduler.eventloop import AsyncIOThreadSafeScheduler

CI = os.getenv("CI") is not None


class TestAsyncIOThreadSafeScheduler(unittest.TestCase):
    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_asyncio_threadsafe_schedule_now(self) -> None:
        loop = asyncio.new_event_loop()
        try:
            scheduler = AsyncIOThreadSafeScheduler(loop)
            now = datetime.now(timezone.utc)
            diff = scheduler.now - now
            assert abs(diff) < timedelta(
                milliseconds=100
            )  # Should be very close to actual time
        finally:
            loop.close()

    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_asyncio_threadsafe_schedule_now_units(self) -> None:
        loop = asyncio.new_event_loop()
        try:

            async def go() -> None:
                scheduler = AsyncIOThreadSafeScheduler(loop)
                diff = scheduler.now
                await asyncio.sleep(0.1)
                diff = scheduler.now - diff
                assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

            loop.run_until_complete(go())
        finally:
            loop.close()

    def test_asyncio_threadsafe_schedule_action(self) -> None:
        loop = asyncio.new_event_loop()
        try:

            async def go() -> None:
                scheduler = AsyncIOThreadSafeScheduler(loop)
                ran = False

                def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
                    nonlocal ran
                    ran = True
                    return None

                def schedule() -> None:
                    scheduler.schedule(action)

                threading.Thread(target=schedule).start()

                await asyncio.sleep(0.1)
                assert ran is True

            loop.run_until_complete(go())
        finally:
            loop.close()

    def test_asyncio_threadsafe_schedule_action_due(self) -> None:
        loop = asyncio.new_event_loop()
        try:

            async def go() -> None:
                scheduler = AsyncIOThreadSafeScheduler(loop)
                starttime = loop.time()
                endtime = None

                def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
                    nonlocal endtime
                    endtime = loop.time()
                    return None

                def schedule() -> None:
                    scheduler.schedule_relative(0.2, action)

                threading.Thread(target=schedule).start()

                await asyncio.sleep(0.3)
                assert endtime is not None
                diff = endtime - starttime
                assert diff > 0.18

            loop.run_until_complete(go())
        finally:
            loop.close()

    def test_asyncio_threadsafe_schedule_action_cancel(self) -> None:
        loop = asyncio.new_event_loop()
        try:

            async def go() -> None:
                ran = False
                scheduler = AsyncIOThreadSafeScheduler(loop)

                def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
                    nonlocal ran
                    ran = True
                    return None

                def schedule() -> None:
                    d = scheduler.schedule_relative(0.05, action)
                    d.dispose()

                threading.Thread(target=schedule).start()

                await asyncio.sleep(0.3)
                assert ran is False

            loop.run_until_complete(go())
        finally:
            loop.close()

    def cancel_same_thread_common(
        self,
        test_body: Any,
    ) -> None:
        update_state: dict[str, Any] = {"ran": False, "dispose_completed": False}

        def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            update_state["ran"] = True
            return None

        # Make the actual test body run in deamon thread, so that in case of
        # failure it doesn't hang indefinitely.
        def thread_target() -> None:
            loop = asyncio.new_event_loop()
            scheduler = AsyncIOThreadSafeScheduler(loop)

            test_body(scheduler, action, update_state)

            async def go() -> None:
                await asyncio.sleep(0.2)

            loop.run_until_complete(go())

        thread = threading.Thread(target=thread_target)
        thread.daemon = True
        thread.start()
        thread.join(0.3)
        assert update_state["dispose_completed"] is True
        assert update_state["ran"] is False

    def test_asyncio_threadsafe_cancel_non_relative_same_thread(self) -> None:
        def test_body(
            scheduler: AsyncIOThreadSafeScheduler,
            action: abc.ScheduledAction[Any],
            update_state: dict[str, Any],
        ) -> None:
            d = scheduler.schedule(action)

            # Test case when dispose is called on thread on which loop is not
            # yet running, and non-relative schedele is used.
            d.dispose()
            update_state["dispose_completed"] = True

        self.cancel_same_thread_common(test_body)

    def test_asyncio_threadsafe_schedule_action_cancel_same_thread(self) -> None:
        def test_body(
            scheduler: AsyncIOThreadSafeScheduler,
            action: abc.ScheduledAction[Any],
            update_state: dict[str, Any],
        ) -> None:
            d = scheduler.schedule_relative(0.05, action)

            # Test case when dispose is called on thread on which loop is not
            # yet running, and relative schedule is used.
            d.dispose()
            update_state["dispose_completed"] = True

        self.cancel_same_thread_common(test_body)

    def test_asyncio_threadsafe_schedule_action_cancel_same_loop(self) -> None:
        def test_body(
            scheduler: AsyncIOThreadSafeScheduler,
            action: abc.ScheduledAction[Any],
            update_state: dict[str, Any],
        ) -> None:
            d = scheduler.schedule_relative(0.1, action)

            def do_dispose() -> None:
                d.dispose()
                update_state["dispose_completed"] = True

            # Test case when dispose is called in loop's callback.
            scheduler._loop.call_soon(do_dispose)

        self.cancel_same_thread_common(test_body)
