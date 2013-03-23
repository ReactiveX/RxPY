from rx.disposables import DisposableEmpty, CompositeDisposable
from datetime import datetime, timedelta

class Scheduler(object):
    def schedule(self, action, state=None):
        raise NotImplementedError

    def schedule_relative(self, action, state=None):
        raise NotImplementedError

    def schedule_absolute(self, state, action):
        raise NotImplementedError

    def invoke_action(self, action, state=None):
        print("invoke_action", action, state)
        action(self, state)
        return DisposableEmpty()
        
    def invoke_rec_immediate(self, scheduler, pair):
        #print "invoke_rec_immediate", scheduler, pair
        state = pair.get('state')
        action = pair.get('action')
        group = CompositeDisposable()
        
        def recursive_action(state1):
            # FIXME: need a better name for this function
            def action2(state2):
                #print "action2", state2
                is_added = False
                is_done = False
                
                def action(scheduler, state=None):
                    #print "action", scheduler1, state3
                    if is_added:
                        group.remove(d)
                    else:
                        is_done = True
                    
                    recursive_action(state)
                    return DisposableEmpty()

                d = scheduler.schedule(action, state2)
                
                if not is_done:
                    group.add(d)
                    is_added = True

            action(action2, state1)
        
        recursive_action(state)
        return group
    
    def schedule_recursive(self, action, state=None):
        #print "schedule_recursive", action, state
        def action2(scheduler, pair):
            return self.invoke_rec_immediate(scheduler, pair)

        return self.schedule(action2, dict(state=state, action=action))

    @classmethod
    def now(cls):
        return datetime.utcnow()

    @classmethod
    def normalize(cls, timespan):
        nospan = timedelta(0)
        if not timespan or timespan < nospan:
            timespan = nospan
        
        return timespan


#Scheduler.immediate = immediatescheduler