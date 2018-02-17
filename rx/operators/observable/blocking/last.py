from typing import Any


def last(self) -> Any:
    """Blocks until the last element emits from a BlockingObservable.

    If no item is emitted when on_completed() is called, an exception is thrown

    Note: This will block even if the underlying Observable is
    asynchronous.

    Returns the last item to be emitted from a BlockingObservable
    """
    last_item = None
    is_empty = True

    for item in self.to_iterable():
        is_empty = False
        last_item = item

    if is_empty:
        raise Exception("No items were emitted")

    return last_item

def last_or_default(self, default_value: Any) -> Any:
    """Blocks until the last element emits from a BlockingObservable.

    If no item is emitted when on_completed() is called, the provided
    default_value will be returned

    Note: This will block even if the underlying Observable is
    asynchronous.

    Keyword arguments:
    default_value -- Value to return if no value has been emitted.

    Returns the last item to be emitted from a BlockingObservable
    """
    last_item = None
    is_empty = True

    for item in self.to_iterable():
        is_empty = False
        last_item = item

    if is_empty:
        return default_value

    return last_item
