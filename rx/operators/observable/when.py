from rx import Observable, AnonymousObserver, AnonymousObservable
from rx.disposables import CompositeDisposable
from rx.internal import extensionclassmethod


@extensionclassmethod(Observable)
def when(cls, *args):
    """Joins together the results from several patterns.

    :param Observable cls: Observable class.
    :param list[Plan] args: A series of plans (specified as a list of as a
        series of arguments) created by use of the Then operator on patterns.
    :returns: Observable sequence with the results form matching several
        patterns.
    :rtype: Observable
    """

    plans = args[0] if len(args) and isinstance(args[0], list) else list(args)

    def subscribe(observer, scheduler=None):
        active_plans = []
        external_subscriptions = {}

        def throw(err):
            for v in external_subscriptions.values():
                v.throw(err)
            observer.throw(err)

        out_observer = AnonymousObserver(observer.send, throw, observer.close)

        def deactivate(active_plan):
            active_plans.remove(active_plan)
            if not len(active_plans):
                observer.close()
        try:
            for plan in plans:
                active_plans.append(plan.activate(external_subscriptions, 
                                                  out_observer, deactivate))
        except Exception as ex:
            Observable.throw(ex).subscribe(observer)

        group = CompositeDisposable()
        for join_observer in external_subscriptions.values():
            join_observer.subscribe()
            group.add(join_observer)

        return group

    return AnonymousObservable(subscribe)
