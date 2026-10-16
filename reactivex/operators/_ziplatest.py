from collections.abc import Callable
from typing import Any

import reactivex
from reactivex import Observable


def zip_latest_(
    *others: Observable[Any],
) -> Callable[[Observable[Any]], Observable[tuple[Any, ...]]]:
    def _zip_latest(source: Observable[Any]) -> Observable[tuple[Any, ...]]:
        return reactivex.zip_latest(source, *others)

    return _zip_latest


__all__ = ["zip_latest_"]
