from rx import Observable
from rx.testing import TestScheduler

class RxException(Exception):
    pass

def test_select_throws():

    # Helper function for raising exceptions within lambdas
    def _raise(ex):
        raise RxException(ex)

    try:
        Observable.returnvalue(1) \
            .select(lambda x, y: x) \
            .subscribe(lambda x: _raise("ex"))
    except RxException:
        pass

    try:
        Observable.throw_exception('ex') \
            .select(lambda x, y: x) \
            .subscribe(on_error=lambda ex: _raise(ex))
    except RxException:
        pass

    try:
        Observable.empty() \
            .select(lambda x, y: x) \
            .subscribe(lambda x: x, lambda ex: ex, lambda: _raise('ex'))
    except RxException:
        pass

    try:
        def subscribe(observer):
            _raise('ex')
        
        Observable.create(subscribe) \
            .select(lambda x: x) \
            .subscribe()
    except RxException:
        pass

def test_select_disposeinsideselector():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(onNext(100, 1), onNext(200, 2), onNext(500, 3), onNext(600, 4))
    invoked = 0
    results = scheduler.createObserver()
    d = SerialDisposable()

    def projection(x):
        nonlocal invoked
        invoked += 1
        if scheduler.clock > 400:
            d.dispose()
        
        return x

    d.disposable(xs.select(projection).subscribe(results));

    def action(scheduler, state):
        return d.dispose()

    scheduler.schedule_absolute(disposed, action)
    scheduler.start()
    results.messages.assertEqual(onNext(100, 1), onNext(200, 2));
    xs.subscriptions.assertEqual(subscribe(0, 500));
    assert invoked == 3
