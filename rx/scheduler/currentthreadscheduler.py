import logging
import threading

from typing import MutableMapping
from weakref import WeakKeyDictionary

from .trampolinescheduler import TrampolineScheduler, _Local as Local


log = logging.getLogger('Rx')


class _Local(threading.local):

    def __init__(self) -> None:
        super().__init__()
        self.local = Local()


class CurrentThreadScheduler(TrampolineScheduler):
    """Represents an object that schedules units of work on the current thread.
    You never want to schedule timeouts using the *CurrentThreadScheduler*
    since that will block the current thread while waiting.

    Please note, there will be at most a single instance per thread -- calls to
    the constructor will just return the same instance if one already exists.

    Conversely, if you pass an instance to another thread, it will effectively
    behave as a separate scheduler, with its own queue. In particular, this
    implies that you can't make assumptions about the execution order of items
    that were scheduled by different threads -- even if they were submitted to
    what superficially appears to be a single scheduler instance.

    If this is not what you want, you might consider using the base class
    :class:`TrampolineScheduler` instead.
    """

    _local = _Local()
    _global: MutableMapping[
        threading.Thread,
        MutableMapping[type, 'CurrentThreadScheduler']
    ] = WeakKeyDictionary()

    @classmethod
    def singleton(cls) -> 'CurrentThreadScheduler':
        thread = threading.current_thread()
        thread_map = CurrentThreadScheduler._global.get(thread)
        if thread_map is None:
            thread_map = WeakKeyDictionary()
            CurrentThreadScheduler._global[thread] = thread_map
        try:
            self = thread_map[cls]
        except KeyError:
            self = super().__new__(cls)
            thread_map[cls] = self
        return self

    def __new__(cls) -> 'CurrentThreadScheduler':
        """Ensure that each thread has at most a single instance."""

        return cls.singleton()

    # pylint: disable=super-init-not-called
    def __init__(self):
        pass  # By design

    def _get_local(self):
        return CurrentThreadScheduler._local.local
