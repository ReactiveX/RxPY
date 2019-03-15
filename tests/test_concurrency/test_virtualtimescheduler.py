import unittest
from datetime import datetime, timedelta
from rx.concurrency import VirtualTimeScheduler
from rx.internal import ArgumentOutOfRangeException


class VirtualSchedulerTestScheduler(VirtualTimeScheduler):
    def __init__(self):
        super().__init__()

    def add(self, absolute, relative):
        return absolute + relative


class TestVirtualTimeScheduler(unittest.TestCase):
    def test_virtual_now(self):
        res = VirtualSchedulerTestScheduler().now - datetime.utcfromtimestamp(0)
        assert(res < timedelta(1000))

    def test_virtual_schedule_action(self):
        ran = [False]
        scheduler = VirtualSchedulerTestScheduler()

        def action(scheduler, state):
            ran[0] = True
        scheduler.schedule(action)

        scheduler.start()
        assert(ran[0])

    def test_virtual_schedule_action_error(self):
        ex = 'ex'
        try:
            scheduler = VirtualSchedulerTestScheduler()

            def action(scheduler, state):
                raise Exception(ex)

            scheduler.schedule(action)
            scheduler.start()
            assert(False)
        except Exception as e:
            self.assertEqual(str(e), ex)

    def test_virtual_schedule_advance_clock_error(self):
        scheduler = VirtualSchedulerTestScheduler()

        try:
            scheduler.sleep(-1)
        except Exception as e:
            assert isinstance(e, ArgumentOutOfRangeException)

        try:
            scheduler.advance_to(scheduler._clock - 1)
        except Exception as e:
            assert isinstance(e, ArgumentOutOfRangeException)
