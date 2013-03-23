from datetime import datetime, timedelta

from rx.concurrency import Scheduler, CurrentThreadScheduler

def test_currentthread_now():
    res = Scheduler.now() - datetime.utcnow()
    assert res < timedelta(milliseconds=1000)


def test_currentthread_scheduleaction():
	scheduler = CurrentThreadScheduler()
	ran = False

	def action(scheduler, state=None):
		nonlocal ran
		ran = True

	scheduler.schedule(action)
	assert ran == True