import unittest
from datetime import datetime, timedelta
from rx.concurrency import VirtualTimeScheduler


class VirtualSchedulerTestScheduler(VirtualTimeScheduler):
    def __init__(self):
        super(VirtualSchedulerTestScheduler, self).__init__()

    @staticmethod
    def comparer(a, b):
        if a > b:
            return 1

        if a < b:
            return -1

        return 0

    def add(self, absolute, relative):
        if not absolute:
            absolute = ''

        return absolute + relative

    def to_datetime_offset(self, absolute):
        if not absolute:
            absolute = ''

        return datetime.fromtimestamp(len(absolute))


class TestVirtualTimeScheduler(unittest.TestCase):
    def test_virtual_now(self):
        res = VirtualSchedulerTestScheduler().now - datetime.fromtimestamp(0)
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
