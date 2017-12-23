from typing import Any
import types

from rx.concurrency import current_thread_scheduler

from .observable import ObservableBase
from .autodetachobserver import AutoDetachObserver
from .anonymousobserver import AnonymousObserver
from .disposable import Disposable
from . import abc


def subscribe(source: ObservableBase, observer:abc.Observer = None,
              scheduler: abc.Scheduler = None):
    """Subscribe an observer to the observable sequence.

    Examples:
    1 - source.subscribe()
    2 - source.subscribe(observer)

    Keyword arguments:
    observer -- [Optional] The object that is to receive
        notifications. You may subscribe using an observer or
        callbacks, not both.

    Return disposable object representing an observer's subscription
        to the observable sequence.
    """

    observer = observer or AnonymousObserver()
    assert isinstance(observer, abc.Observer) or isinstance(observer, types.GeneratorType)

    auto_detach_observer = AutoDetachObserver(observer)

    def fix_subscriber(subscriber):
        """Fixes subscriber to make sure it returns a Disposable instead
        of None or a dispose function"""

        if not hasattr(subscriber, "dispose"):
            subscriber = Disposable.create(subscriber)

        return subscriber

    def set_disposable(_: abc.Scheduler=None, __: Any=None):
        try:
            subscriber = source._subscribe_core(auto_detach_observer, scheduler)
        except Exception as ex:  # By design. pylint: disable=W0703
            if not auto_detach_observer.fail(ex):
                raise
        else:
            auto_detach_observer.disposable = fix_subscriber(subscriber)

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

    # Hide the identity of the auto detach observer
    return Disposable.create(auto_detach_observer.dispose)
