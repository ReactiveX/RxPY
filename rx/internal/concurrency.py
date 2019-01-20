
class RLock(object):
    """Dummy lock object for schedulers that don't need locking"""

    def locked(self):
        return False

    def __enter__(self):
        """Context management protocol"""
        pass

    def __exit__(self, type, value, traceback):
        """Context management protocol"""
        pass


class Event(object):
    def is_set(self):
        return False

    def set(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def wait(self):
        raise NotImplementedError


class Condition(object):
    def wait(self):
        raise NotImplementedError

    def aquire(self):
        raise NotImplementedError

    def release(self):
        raise NotImplementedError

    def notify(self, n=1):
        raise NotImplementedError

    def notify_all(self):
        raise NotImplementedError


def synchronized(lock):
    """A decorator for synchronizing access to a given function."""

    def wrapper(fn):
        def inner(*args, **kw):
            with lock:
                return fn(*args, **kw)
        return inner
    return wrapper
