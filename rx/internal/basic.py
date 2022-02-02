from datetime import datetime
from typing import Any, NoReturn, Union


# Defaults
def noop(*args: Any, **kw: Any):
    """No operation. Returns nothing"""
    pass


def identity(x: Any) -> Any:
    """Returns argument x"""
    return x


def default_now() -> datetime:
    return datetime.utcnow()


def default_comparer(x: Any, y: Any) -> bool:
    return x == y


def default_sub_comparer(x: Any, y: Any) -> Any:
    return x - y


def default_key_serializer(x: Any) -> str:
    return str(x)


def default_error(err: Union[Exception, str]) -> NoReturn:
    if isinstance(err, BaseException):
        raise err

    raise Exception(err)
