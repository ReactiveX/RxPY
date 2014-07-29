from rx import AnonymousObservable, Observable

class GroupedObservable(Observable):

    def __init__(source, enable_queue):
        super(Observable, self).__init__(self.subscribe)
        
        self.subject = ControlledSubject(enable_queue)
        self.source = source.multicast(this.subject).ref_count()
    
    def subscribe(self, observer):
        return self.source.subscribe(observer)
      
    def request(self, number_of_items):
        if number_of_items is None:
            number_of_items = -1
        return self.subject.request(number_of_items)
