from reactivex import Observable, abc, timer, typing


def interval_(
    period: typing.RelativeTime, scheduler: abc.SchedulerBase | None = None
) -> Observable[int]:
    return timer(period, period, scheduler)


__all__ = ["interval_"]
