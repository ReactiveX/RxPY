from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable

from rx.disposables import Disposable
from rx.concurrency import ImmediateScheduler

class ObservableCreation(Observable, metaclass=ObservableMeta):

    @classmethod
    def create(cls, subscribe):
        def _subscribe(observer):
            return Disposable.create(subscribe(observer))
        
        return AnonymousObservable(_subscribe)

    @classmethod
    def create_with_disposable(cls, subscribe):
        return cls(subscribe)

    @classmethod
    def defer(cls, observable_factory):
        def subscribe(observer):
            result = None
            try:
                result = observable_factory()
            except Exception as ex:
                return Observable.throw(ex).subscribe(observer)
            
            return result.subscribe(observer)
        return AnonymousObservable(subscribe)

    @classmethod
    def empty(cls, scheduler=None):
        scheduler = scheduler or ImmediateScheduler()
    
        def subscribe(observer):
            def action(scheduler, state):
                observer.on_completed()

            return scheduler.schedule(action)
        return AnonymousObservable(subscribe)

# var observableFromArray = Observable.fromArray = function (array, scheduler) {
#     scheduler || (scheduler = currentThreadScheduler)
#     return new AnonymousObservable(function (observer) {
#         var count = 0
#         return scheduler.scheduleRecursive(function (self) {
#             if (count < array.length) {
#                 observer.onNext(array[count++])
#                 self()
#             } else {
#                 observer.onCompleted()
#             }
#         })
#     })
# }

# Observable.generate = function (initialState, condition, iterate, resultSelector, scheduler) {
#     scheduler || (scheduler = currentThreadScheduler)
#     return new AnonymousObservable(function (observer) {
#         var first = true, state = initialState
#         return scheduler.scheduleRecursive(function (self) {
#             var hasResult, result
#             try {
#                 if (first) {
#                     first = false
#                 } else {
#                     state = iterate(state)
#                 }
#                 hasResult = condition(state)
#                 if (hasResult) {
#                     result = resultSelector(state)
#                 }
#             } catch (exception) {
#                 observer.onError(exception)
#                 return
#             }
#             if (hasResult) {
#                 observer.onNext(result)
#                 self()
#             } else {
#                 observer.onCompleted()
#             }
#         })
#     })
# }
    @classmethod
    def never(cls):
        def subscribe(observer):
            return Disposable.empty()

        return AnonymousObservable(subscribe)

    @classmethod
    def range(cls, start, count, scheduler=None):
        scheduler = scheduler or CurrentThreadScheduler()
        
        def subscribe(observer):
            def action(scheduler, i):
                #print("Observable:range:subscribe:action", scheduler, i)
                if i < count:
                    observer.on_next(start + i)
                    scheduler(i + 1)
                else:
                    #print "completed"
                    observer.on_completed()
                
            return scheduler.schedule_recursive(action, 0)
        return AnonymousObservable(subscribe)

    @classmethod
    def repeat(cls, value, repeat_count=None, scheduler=None):
        scheduler = scheduler or CurrentThreadScheduler()
        if repeat_count is None:
            repeat_count = -1
        
        return AnonymousObservable.return_value(value, scheduler).repeat(repeat_count)

    @classmethod
    def return_value(cls, value, scheduler=None):
        scheduler = scheduler or ImmediateScheduler()

        def subscribe(observer):
            def action(scheduler, state=None):
                observer.on_next(value)
                observer.on_completed()

            return scheduler.schedule(action)
        return AnonymousObservable(subscribe)

    @classmethod
    def throw_exception(cls, exception, scheduler=None):
        scheduler = scheduler or ImmediateScheduler()
        
        exception = Exception(exception) if type(exception) is Exception else exception

        def subscribe(observer):
            def action(scheduler, state):
                observer.on_error(exception)

            return scheduler.schedule(action)
        return AnonymousObservable(subscribe)

    @classmethod
    def using(cls, resource_factory, observable_factory):
        def subscribe(observer):
            disposable = Disposable.empty()
            try:
                resource = resource_factory()
                if resource:
                    disposable = resource
                
                source = observable_factory(resource)
            except Exception as exception:
                return CompositeDisposable(Observable.throw(exception).subscribe(observer), disposable)
            
            return CompositeDisposable(source.subscribe(observer), disposable)
        return AnonymousObservable(subscribe)
