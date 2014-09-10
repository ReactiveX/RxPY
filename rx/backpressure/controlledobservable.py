from rx import AnonymousObservable, Observable

from .controlledsubject import ControlledSubject

class ControlledObservable(Observable):

    def __init__(self, source, enable_queue):
        super(ControlledObservable, self).__init__(self._subscribe)
        
        self.subject = ControlledSubject(enable_queue)
        self.source = source.multicast(self.subject).ref_count()
    
    def _subscribe(self, observer):
        return self.source.subscribe(observer)
      
    def request(self, number_of_items):
        if number_of_items is None:
            number_of_items = -1
        return self.subject.request(number_of_items)
