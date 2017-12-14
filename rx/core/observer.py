from typing import Generic, TypeVar
from . import bases

T_in = TypeVar('T_in', contravariant=True)


class Observer(Generic[T_in], extra=bases.Observer):
    __slots__ = ()
