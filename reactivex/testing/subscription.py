import sys
from typing import Any, Optional


class Subscription:
    def __init__(self, start: int, end: Optional[int] = None):
        self.subscribe = start
        self.unsubscribe = end or sys.maxsize

    def equals(self, other: Any) -> bool:
        return (
            self.subscribe == other.subscribe and self.unsubscribe == other.unsubscribe
        )

    def __eq__(self, other: Any) -> bool:
        return self.equals(other)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        unsubscribe = (
            "Infinite" if self.unsubscribe == sys.maxsize else self.unsubscribe
        )
        return "(%s, %s)" % (self.subscribe, unsubscribe)
