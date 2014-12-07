from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.internal import extends


@extends(Observable)
class Create(object):

    @classmethod
    def create(cls, subscribe):
        return AnonymousObservable(subscribe)

    # Deprecated alias
    create_with_disposable = create
