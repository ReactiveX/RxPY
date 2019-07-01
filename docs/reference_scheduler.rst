.. _reference_scheduler:

Schedulers
===========

.. automodule:: rx.scheduler
    :members: CatchScheduler, CurrentThreadScheduler, EventLoopScheduler,
                HistoricalScheduler, ImmediateScheduler, NewThreadScheduler,
                ThreadPoolScheduler, TimeoutScheduler, TrampolineScheduler,
                VirtualTimeScheduler

.. automodule:: rx.scheduler.eventloop
    :members: AsyncIOScheduler, AsyncIOThreadSafeScheduler, EventletScheduler,
                GEventScheduler, IOLoopScheduler, TwistedScheduler

.. automodule:: rx.scheduler.mainloop
    :members: GtkScheduler, PyGameScheduler, QtScheduler,
                TkinterScheduler, WxScheduler
