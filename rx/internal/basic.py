from typing import Any
from datetime import datetime


# Defaults
def noop(*args, **kw):
    """No operation. Returns nothing"""
    pass


def identity(x: Any) -> Any:
    """Returns argument x"""
    return x


def default_now() -> datetime:
    return datetime.utcnow()


def default_comparer(x: Any, y: Any) -> bool:
    return x == y


def default_sub_comparer(x, y):
    return x - y


def default_key_serializer(x: Any) -> str:
    return str(x)


def default_error(err) -> Exception:
    if isinstance(err, BaseException):
        raise err
    else:
        raise Exception(err)
