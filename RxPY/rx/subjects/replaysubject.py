# Replay Subject
class ReplaySubject(Observable):
    """Represents an object that is both an observable sequence as well as an 
    observer. Each notification is broadcasted to all subscribed and future 
    observers, subject to buffer trimming policies.
    """ 

    class RemovableDisposable(object):
        def __init__(self, subject, observer):
            self.subject = subject
            self.observer = observer
    
        def dispose(self):
            self.observer.dispose()
            if not self.subject.is_disposed:
                idx = self.subject.observers.indexOf(self.observer)
                self.subject.observers.splice(idx, 1)
        
    def __init__(self, bufferSize, window, scheduler):
        """Initializes a new instance of the ReplaySubject class with the 
        specified buffer size, window and scheduler.
     
        Keyword arguments:
        {Number} [bufferSize] Maximum element count of the replay buffer.
        {Number} [window] Maximum time length of the replay buffer.
        scheduler -- [Optional] Scheduler the observers are invoked on.
        """
    
        self.bufferSize = bufferSize == None ? Number.MAX_VALUE : bufferSize
        self.window = window == None ? Number.MAX_VALUE : window
        self.scheduler = scheduler || currentThreadScheduler
        self.q = []
        self.observers = []
        self.is_stopped = false
        self.is_disposed = false
        self.has_error = false
        self.error = None

        super(ReplaySubject, self).__init__(self.subscribe)

    def subscribe(self, observer):
        so = ScheduledObserver(self.scheduler, observer),
        subscription = RemovableDisposable(self, so)
        self.check_disposed()
        self._trim(self.scheduler.now())
        self.observers.push(so)

        n = self.q.length

        for item in self.q:
            so.on_next(item.value)

        if self.has_error:
            n += 1
            so.on_error(self.error)
        elif self.is_stopped:
            n += 1
            so.on_completed()

        so.ensure_active(n)
        return subscription
    
    def _trim: (self, now):
            while self.q.length > self.bufferSize:
                self.q.shift()
            
            while self.q.length > 0 and (now - self.q[0].interval) > self.window):
                self.q.shift()

        def on_next(self, value):
            self.check_disposed()
            if not self.is_stopped:
                now = self.scheduler.now()
                self.q.push({ interval: now, value: value })
                self._trim(now)

                o = self.observers[:]
                for (i = 0, len = o.length i < len i++) {
                    observer = o[i]
                    observer.on_next(value)
                    observer.ensure_active()
        
        def on_error(self, error):
            self.check_disposed()
            if not self.is_stopped:
                self.is_stopped = true
                self.error = error
                self.has_error = true
                now = self.scheduler.now()
                self._trim(now)
                o = self.observers[:]
                for (i = 0, len = o.length i < len i++) {
                    observer = o[i]
                    observer.on_error(error)
                    observer.ensure_active()
                }
                self.observers = []
            
        def on_completed(self):
            self.check_disposed()
            if not self.is_stopped:
                self.is_stopped = true
                now = self.scheduler.now()
                self._trim(now)
                o = self.observers[:]
                for (i = 0, len = o.length i < len i++) {
                    observer = o[i]
                    observer.on_completed()
                    observer.ensure_active()
                
                self.observers = []
            
        def dispose(self):
            self.is_disposed = true
            self.observers = None
        
