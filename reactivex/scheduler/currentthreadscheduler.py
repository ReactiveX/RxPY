import logging
from threading import Thread, current_thread, local
from typing import MutableMapping
from weakref import WeakKeyDictionary

from .trampoline import Trampoline
from .trampolinescheduler import TrampolineScheduler

log = logging.getLogger("Rx")


class CurrentThreadScheduler(TrampolineScheduler):
    """Represents an object that schedules units of work on the current thread.
    You should never schedule timeouts using the *CurrentThreadScheduler*, as
    that will block the thread while waiting.

    Each instance manages a number of trampolines (and queues), one for each
    thread that calls a *schedule* method. These trampolines are automatically
    garbage-collected when threads disappear, because they're stored in a weak
    key dictionary.
    """

    _global: MutableMapping[
        type, MutableMapping[Thread, "CurrentThreadScheduler"]
    ] = WeakKeyDictionary()

    @classmethod
    def singleton(cls) -> "CurrentThreadScheduler":
        """
        Obtain a singleton instance for the current thread. Please note, if you
        pass this instance to another thread, it will effectively behave as
        if it were created by that other thread (separate trampoline and queue).

        Returns:
            The singleton *CurrentThreadScheduler* instance.
        """
        thread = current_thread()
        class_map = CurrentThreadScheduler._global.get(cls)
        if class_map is None:
            class_map_: MutableMapping[
                Thread, "CurrentThreadScheduler"
            ] = WeakKeyDictionary()
            CurrentThreadScheduler._global[cls] = class_map_
        else:
            class_map_ = class_map
        try:
            self = class_map_[thread]
        except KeyError:
            self = CurrentThreadSchedulerSingleton()
            class_map_[thread] = self
        return self

    # pylint: disable=super-init-not-called
    def __init__(self) -> None:
        self._tramps: MutableMapping[Thread, Trampoline] = WeakKeyDictionary()

    def get_trampoline(self) -> Trampoline:
        thread = current_thread()
        tramp = self._tramps.get(thread)
        if tramp is None:
            tramp = Trampoline()
            self._tramps[thread] = tramp
        return tramp


class _Local(local):
    def __init__(self) -> None:
        super().__init__()
        self.tramp = Trampoline()


class CurrentThreadSchedulerSingleton(CurrentThreadScheduler):

    _local = _Local()

    # pylint: disable=super-init-not-called
    def __init__(self) -> None:
        pass

    def get_trampoline(self) -> Trampoline:
        return CurrentThreadSchedulerSingleton._local.tramp
