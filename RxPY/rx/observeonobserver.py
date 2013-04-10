from rx.scheduledobserver import ScheduledObserver

class ObserveOnObserver(ScheduledObserver):
    def __init__(self, scheduler, observer):
        super(ObserveOnObserver, self).__init__(scheduler, observer)

    def next(self, value):
        super(ObserveOnObserver, self).next(value);
        self.ensure_active()
    
    def error(self, e):
        super(ObserveOnObserver, self).error(e)
        self.ensure_active()
    
    def completed(self):
        super(ObserveOnObserver, self).completed()
        self.ensure_active()
    