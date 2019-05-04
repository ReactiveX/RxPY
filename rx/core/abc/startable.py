from abc import ABC, abstractmethod


class Startable(ABC):
    """Abstract base class for Thread- and Process-like objects."""
    __slots__ = ()

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError
