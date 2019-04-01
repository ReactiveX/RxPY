.. _reference_scheduler:

Schedulers
===========

.. automodule:: rx.concurrency
    :members: ImmediateScheduler, CurrentThreadScheduler, VirtualTimeScheduler,
                TimeoutScheduler, NewThreadScheduler, ThreadPoolScheduler,
                EventLoopScheduler, HistoricalScheduler, CatchScheduler

.. automodule:: rx.concurrency.mainloopscheduler
    :members: AsyncIOScheduler, IOLoopScheduler, GEventScheduler,
                GtkScheduler, TwistedScheduler, TkinterScheduler,
                PyGameScheduler, QtScheduler, WxScheduler,
                EventLetEventScheduler