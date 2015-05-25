from rx.concurrency import current_thread_scheduler
from rx.disposables import Disposable
from .autodetachobserver import AutoDetachObserver
from .observable import Observable


class AnonymousObservable(Observable):
    """Class to create an Observable instance from a delegate-based
    implementation of the Subscribe method."""

    def __init__(self, subscribe):
        """Creates an observable sequence object from the specified
        subscription function.

        Keyword arguments:
        :param types.FunctionType subscribe: Subscribe method implementation.
        """

        def _subscribe(observer):
            """Decorator for subscribe. It wraps the observer in an
            AutoDetachObserver and fixes the returned disposable"""

            def fix_subscriber(subscriber):
                """Fixes subscriber to make sure it returns a Disposable instead
                of None or a dispose function"""

                if not hasattr(subscriber, "dispose"):
                    subscriber = Disposable(subscriber)

                return subscriber

            def set_disposable(scheduler=None, value=None):
                try:
                    auto_detach_observer.disposable = fix_subscriber(subscribe(auto_detach_observer))
                except Exception as ex:
                    if not auto_detach_observer.fail(ex):
                        raise ex

            auto_detach_observer = AutoDetachObserver(observer)

            # Subscribe needs to set up the trampoline before for subscribing.
            # Actually, the first call to Subscribe creates the trampoline so
            # that it may assign its disposable before any observer executes
            # OnNext over the CurrentThreadScheduler. This enables single-
            # threaded cancellation
            # https://social.msdn.microsoft.com/Forums/en-US/eb82f593-9684-4e27-
            # 97b9-8b8886da5c33/whats-the-rationale-behind-how-currentthreadsche
            # dulerschedulerequired-behaves?forum=rx
            if current_thread_scheduler.schedule_required():
                current_thread_scheduler.schedule(set_disposable)
            else:
                set_disposable()

            return auto_detach_observer

        super(AnonymousObservable, self).__init__(_subscribe)
