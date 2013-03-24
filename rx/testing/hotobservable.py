class HotObservable(Observable):
    def __init__(self, scheduler, messages):
        Observable.__init__(self, subscribe)

        observable = this
        self.scheduler = scheduler
        self.messages = messages
        self.subscriptions = []
        self.observers = []
        
        for message = self.messages:
            notification = message.value

            (function (innerNotification) {
                scheduler.scheduleAbsoluteWithState(null, message.time, function () {
                    for (var j = 0; j < observable.observers.length; j++) {
                        innerNotification.accept(observable.observers[j]);
                    }
                    return disposableEmpty;
                });
            })(notification);
    
    def subscribe(self, observer):
        observable = self
        self.observers.append(observer)
        self.subscriptions.push(new Subscription(this.scheduler.clock))
        var index = this.subscriptions.length - 1

        def action():
            var idx = observable.observers.indexOf(observer)
            observable.observers.splice(idx, 1)
            observable.subscriptions[index] = Subscription(observable.subscriptions[index].subscribe, observable.scheduler.clock)

        return Disposable.create(action)

    