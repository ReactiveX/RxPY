
class NoLock(object):
    """Dummy lock object for schedulers that don't need locking"""

    def locked(self):
        return False

    def __enter__(self):
        """Context management protocol"""
        pass

    def __exit__(self, type, value, traceback):
        """Context management protocol"""
        pass