from threading import Timer
from datetime import datetime, timedelta

from rx.disposables import Disposable, CompositeDisposable

class Scheduler(object):
    def schedule(self, action, state=None):
        raise NotImplementedError

    def schedule_relative(self, duetime, action, state=None):
        raise NotImplementedError

    def schedule_absolute(self, duetime, action, state=None):
        raise NotImplementedError

    def invoke_action(self, action, state=None):
        #print("invoke_action", action, state)
        
        action(self, state)
        return Disposable.empty()

    def schedule_periodic(self, period, action, state=None):
        """Schedules a periodic piece of work by dynamically discovering the 
        scheduler's capabilities. 
     
        Keyword parameters:
        period -- Period for running the work periodically.
        action -- Action to be executed.
        state -- [Optional] Initial state passed to the action upon the first 
            iteration.
     
        Returns the disposable object used to cancel the scheduled recurring 
        action (best effort).
        """

        period /= 1000.0
        timer = None
        s = state
        
        def interval():
            nonlocal timer, s
            s = action(s)
            
            timer = Timer(period, interval)
            timer.start()

        timer = Timer(period, interval)
        timer.start()
        
        def dispose():
            timer.cancel()

        return Disposable(dispose)

    def invoke_rec_immediate(self, scheduler, pair):
        #print "invoke_rec_immediate", scheduler, pair
        state = pair.get('state')
        action = pair.get('action')
        group = CompositeDisposable()
        
        def recursive_action(state1):
            # FIXME: need a better name for this function
            def action2(state2=None):
                #print "action2", state2
                is_added = False
                is_done = False
                
                def action(scheduler, state=None):
                    nonlocal is_done

                    #print "action", scheduler1, state3
                    if is_added:
                        group.remove(d)
                    else:
                        is_done = True
                    
                    recursive_action(state)
                    return Disposable.empty()

                d = scheduler.schedule(action, state2)
                
                if not is_done:
                    group.add(d)
                    is_added = True

            action(action2, state1)
        
        recursive_action(state)
        return group
    
    def invoke_rec_date(self, scheduler, pair, method):
        state = pair.get('first') 
        action = pair.get('second')
        group = CompositeDisposable()
        
        def recursive_action(state1):
            def action1(state2, duetime1):
                is_added, is_done = False, False

                def action2(scheduler1, state3):
                    nonlocal is_done

                    if is_added:
                        group.remove(d)
                    else:
                        is_done = True
                    
                    recursive_action(state3)
                    return Disposable.empty()
                
                d = getattr(scheduler, method)(duetime1, action2, state2)
                if not is_done:
                    group.add(d)
                    is_added = True
                
            action(state1, action1)
        recursive_action(state)
        return group

    def schedule_recursive(self, action, state=None):
        #print "schedule_recursive", action, state
        def action2(scheduler, pair):
            return self.invoke_rec_immediate(scheduler, pair)

        return self.schedule(action2, dict(state=state, action=action))

    def schedule_recursive_relative(self, duetime, action, state=None):
        def action1(s, p):
            print ("Scheduler:schedule_recursive_relative:action()")
            return self.invoke_rec_date(s, p, 'schedule_relative')
        return self.schedule_relative(duetime, action1, state={ "first": state, "second": action })

    def schedule_recursive_with_relative(self, duetime, action):
        def action1(_action, this=None):
            def func(dt):
                this(_action, dt)
            _action(func)
        return self.schedule_recursive_with_relative_and_state(action, duetime, action1)

    def schedule_recursive_with_relative_and_state(self, state, duetime, action):
        def action1(s, p):
            return self.invoke_rec_date(s, p, 'schedule_relative')

        return self.schedule_relative(duetime, action1, state={ "first": state, "second": action })

    @classmethod
    def now(cls):
        return datetime.utcnow()

    @classmethod
    def normalize(cls, timespan):
        nospan = 0 if isinstance(timespan, int) else timedelta(0)
        #timespan = timespan if isinstance(timespan, timedelta) else timedelta(milliseconds=timespan)
        if not timespan or timespan < nospan:
            timespan = nospan
        
        return timespan


#Scheduler.immediate = immediatescheduler