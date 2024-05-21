from datetime import datetime, timezone
from typing import Any, NoReturn, TypeVar, Union

_T = TypeVar("_T")


def noop(*args: Any, **kw: Any) -> None:
    """No operation. Returns nothing"""


def identity(x: _T) -> _T:
    """Returns argument x"""
    return x


def default_now() -> datetime:
    return datetime.now(timezone.utc)


def default_comparer(x: _T, y: _T) -> bool:
    return x == y


def default_sub_comparer(x: Any, y: Any) -> Any:
    return x - y


def default_key_serializer(x: Any) -> str:
    return str(x)


def default_error(err: Union[Exception, str]) -> NoReturn:
    if isinstance(err, BaseException):
        raise err

    raise Exception(err)
