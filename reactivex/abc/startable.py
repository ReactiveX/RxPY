from abc import ABC, abstractmethod


class StartableBase(ABC):
    """Abstract base class for Thread- and Process-like objects."""

    __slots__ = ()

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError


__all__ = ["StartableBase"]
