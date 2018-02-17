from rx.testing import ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass


# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)



# test("Rx.Observable.catchException() does not lose subscription to underlying observable", 12, function () {
#     var subscribes = 0,
#             unsubscribes = 0,
#             tracer = Rx.Observable.create(function (observer) { ++subscribes return function () { ++unsubscribes } ,
#             s

#     // Try it without catchException()
#     s = tracer.subscribe()
#     strictEqual(subscribes, 1, "1 subscribes")
#     strictEqual(unsubscribes, 0, "0 unsubscribes")
#     s.dispose()
#     strictEqual(subscribes, 1, "After dispose: 1 subscribes")
#     strictEqual(unsubscribes, 1, "After dispose: 1 unsubscribes")

#     // Now try again with catchException(Observable):
#     subscribes = unsubscribes = 0
#     s = tracer.catchException(Rx.Observable.never()).subscribe()
#     strictEqual(subscribes, 1, "catchException(Observable): 1 subscribes")
#     strictEqual(unsubscribes, 0, "catchException(Observable): 0 unsubscribes")
#     s.dispose()
#     strictEqual(subscribes, 1, "catchException(Observable): After dispose: 1 subscribes")
#     strictEqual(unsubscribes, 1, "catchException(Observable): After dispose: 1 unsubscribes")

#     // And now try again with catchException(function()):
#     subscribes = unsubscribes = 0
#     s = tracer.catchException(function () { return Rx.Observable.never() .subscribe()
#     strictEqual(subscribes, 1, "catchException(function): 1 subscribes")
#     strictEqual(unsubscribes, 0, "catchException(function): 0 unsubscribes")
#     s.dispose()
#     strictEqual(subscribes, 1, "catchException(function): After dispose: 1 subscribes")
#     strictEqual(unsubscribes, 1, "catchException(function): After dispose: 1 unsubscribes") // this one FAILS (unsubscribes is 0)
#

if __name__ == '__main__':
    test_combine_latest_return_empty()
