import unittest
from datetime import timedelta
from typing import Optional

from reactivex import typing
from reactivex.disposable import Disposable
from reactivex.internal.basic import default_now
from reactivex.scheduler.scheduleditem import ScheduledItem
from reactivex.scheduler.scheduler import Scheduler


class ScheduledItemTestScheduler(Scheduler):
    def __init__(self):
        super()
        self.action = None
        self.state = None
        self.disposable = None

    def invoke_action(self, action, state):
        self.action = action
        self.state = state
        self.disposable = super().invoke_action(action, state)
        return self.disposable

    def schedule(self, action, state):
        pass

    def schedule_relative(self, duetime, action, state):
        pass

    def schedule_absolute(self, duetime, action, state):
        pass


class TestScheduledItem(unittest.TestCase):
    def test_scheduleditem_invoke(self):
        scheduler = ScheduledItemTestScheduler()
        disposable = Disposable()
        state = 42
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True
            return disposable

        item = ScheduledItem(scheduler, state, action, default_now())

        item.invoke()

        assert ran is True
        assert item.disposable.disposable is disposable
        assert scheduler.disposable is disposable
        assert scheduler.state is state
        assert scheduler.action is action

    def test_scheduleditem_cancel(self):
        scheduler = ScheduledItemTestScheduler()

        item = ScheduledItem(scheduler, None, lambda s, t: None, default_now())

        item.cancel()

        assert item.disposable.is_disposed
        assert item.is_cancelled()

    def test_scheduleditem_compare(self):
        scheduler = ScheduledItemTestScheduler()

        duetime1 = default_now()
        duetime2 = duetime1 + timedelta(seconds=1)

        item1 = ScheduledItem(scheduler, None, lambda s, t: None, duetime1)
        item2 = ScheduledItem(scheduler, None, lambda s, t: None, duetime2)
        item3 = ScheduledItem(scheduler, None, lambda s, t: None, duetime1)

        assert item1 < item2
        assert item2 > item3
        assert item1 == item3
