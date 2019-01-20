def synchronized(lock):
    """A decorator for synchronizing access to a given function."""

    def wrapper(fn):
        def inner(*args, **kw):
            with lock:
                return fn(*args, **kw)
        return inner
    return wrapper
