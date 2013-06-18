import logging

from rx import AnonymousObservable, Observable
from rx.internal import noop
from rx.observable import ObservableMeta
from rx.observeonobserver import ObserveOnObserver
from rx.disposables import SingleAssignmentDisposable, SerialDisposable, CompositeDisposable

log = logging.getLogger("Rx")

class ObservableCoincidence(Observable, metaclass=ObservableMeta):

     def join(self, right, left_duration_selector, right_duration_selector, result_selector):
        """Correlates the elements of two sequences based on overlapping durations.
    
        Keyword arguments:
        right -- The right observable sequence to join elements for.
        left_duration_selector -- A function to select the duration (expressed 
            as an observable sequence) of each element of the left observable 
            sequence, used to determine overlap.
        right_duration_selector -- A function to select the duration (expressed 
            as an observable sequence) of each element of the right observable 
            sequence, used to determine overlap.
        result_selector -- A function invoked to compute a result element for 
            any two overlapping elements of the left and right observable 
            sequences. The parameters passed to the function correspond with 
            the elements from the left and right source sequences for which 
            overlap occurs.
        
        Return an observable sequence that contains result elements computed 
        from source elements that have an overlapping duration.
        """   

        left = self

        def subscribe(observer):
            group = CompositeDisposable()
            left_done = False
            left_map = dict()
            left_id = 0
            right_done = False
            right_map = dict()
            right_id = 0
            
            def on_next_left(value):
                nonlocal left_id

                duration = None
                current_id = left_id
                left_id += 1
                md = SingleAssignmentDisposable()
                left_map[current_id] = value
                group.add(md)

                def expire():
                    if current_id in left_map:
                        del left_map[current_id]
                    if not len(left_map) and left_done:
                        observer.on_completed()
                
                    return group.remove(md)
                
                try:
                    duration = left_duration_selector(value)
                except Exception as exception:
                    log.error("*** Exception: %s" % exception)
                    observer.on_error(exception)
                    return
                
                md.disposable = duration.take(1).subscribe(noop, observer.on_error, lambda: expire())
                values = right_map.values()
                for val in values:
                    try:
                        result = result_selector(value, val)
                    except Exception as exception:
                        log.error("*** Exception: %s" % exception)
                        observer.on_error(exception)
                        return
                    
                    observer.on_next(result)
                
            def on_completed_left():
                nonlocal left_done

                left_done = True
                if right_done or not len(left_map):
                    observer.on_completed()
                
            group.add(left.subscribe(on_next_left, observer.on_error, on_completed_left))

            def on_next_right(value):
                nonlocal right_id

                duration = None
                current_id = right_id
                right_id += 1
                md = SingleAssignmentDisposable()
                right_map[current_id] = value
                group.add(md)

                def expire():
                    if current_id in right_map:
                        del right_map[current_id]
                    if not len(right_map) and right_done:
                        observer.on_completed()
                        
                    return group.remove(md)
                
                try:
                    duration = right_duration_selector(value)
                except Exception as exception:
                    log.error("*** Exception: %s" % exception)
                    observer.on_error(exception)
                    return
                
                md.disposable = duration.take(1).subscribe(noop, observer.on_error, lambda: expire())
                values = left_map.values()
                for val in values:
                    try:
                        result = result_selector(val, value)
                    except Exception as exception:
                        log.error("*** Exception: %s" % exception)
                        observer.on_error(exception)
                        return
                    
                    observer.on_next(result)
                
            def on_completed_right():
                nonlocal right_done

                right_done = True
                if left_done or not len(right_map):
                    observer.on_completed()
                
            group.add(right.subscribe(on_next_right, observer.on_error, on_completed_right))
            return group
        
        return AnonymousObservable(subscribe)
    

#     def group_join(self, right, left_duration_selector, right_duration_selector, result_selector):
#         """Correlates the elements of two sequences based on overlapping 
#         durations, and groups the results.
     
#         Keyword arguments:
#         right -- The right observable sequence to join elements for.
#         left_duration_selector -- A function to select the duration (expressed 
#             as an observable sequence) of each element of the left observable 
#             sequence, used to determine overlap.
#         right_duration_selector -- A function to select the duration (expressed
#             as an observable sequence) of each element of the right observable 
#             sequence, used to determine overlap.
#         result_selector -- A function invoked to compute a result element for 
#             any element of the left sequence with overlapping elements from the 
#             right observable sequence. The first parameter passed to the 
#             function is an element of the left sequence. The second parameter 
#             passed to the function is an observable sequence with elements from 
#             the right sequence that overlap with the left sequence's element.
    
#         Returns an observable sequence that contains result elements computed 
#         from source elements that have an overlapping duration.   
#         """
#         left = self

#         def subscribe(observer):
#             nothing = lambda _: None
#             group = CompositeDisposable()
#             r = RefCountDisposable(group)
#             left_map = dict()
#             right_map = dict()
#             left_iD = 0
#             right_id = 0

#             group.add(left.subscribe(
#                 function (value) {
#                     s = Subject()
#                     _id = left_iD += 1
#                     left_map.add(_id, s)
#                     i, len, left_values, right_values

#                     result
#                     try:
#                         result = result_selector(value, addRef(s, r))
#                     except Exception as e:
#                         left_values = left_map.getValues()
#                         for left_value in left_values:
#                             left_value.on_error(e)
                        
#                         observer.on_error(e)
#                         return
                    
#                     observer.on_next(result)

#                     right_values = right_map.getValues()
#                     for right_value in right_values:
#                         s.on_next(right_value)
                    
#                     md = SingleAssignmentDisposable()
#                     group.add(md)

#                     def expire():
#                         if left_map.remove(id):
#                             s.on_completed()
                        
#                         group.remove(md)
                    
#                     try:
#                         duration = left_duration_selector(value)
#                     except Exception as e:
#                         left_values = left_map.getValues()
#                         for left_value in left_values:
#                             left_value.on_error(e)
                        
#                         observer.on_error(e)
#                         return
                    
#                     def on_error(e):
#                         left_values = left_map.getValues()
#                         for left_value in left_values:
#                             left_value.on_error(e)
                        
#                         observer.on_error(e)
                        
#                     md.disposable = duration.take(1).subscribe(
#                         nothing,
#                         on_error,
#                         expire)
                
#                 ,
#                 function (e) {
#                     left_values = left_map.getValues()
#                     for left_value in left_values:
#                         left_value.on_error(e)
                    
#                     observer.on_error(e)
#                 ,
#                 observer.on_completed.bind(observer)))

#             def on_next(value):
#                 left_values, i, len
#                 id = right_id += 1
#                 right_map.add(id, value)

#                 md = SingleAssignmentDisposable()
#                 group.add(md)

#                 def expire():
#                     right_map.remove(id)
#                     group.remove(md)
                

#                 try:
#                     duration = right_duration_selector(value)
#                 except Exception as e:
#                     left_values = left_map.getValues()
#                     for left_value in left_values:
#                         left_value.on_error(e)
                    
#                     observer.on_error(e)
#                     return
                
#                 md.disposable = duration.take(1).subscribe(
#                     nothing,
#                     function (e) {
#                         left_values = left_map.getValues()
#                         for left_value in left_map:
#                             left_value.on_error(e)
                        
#                         observer.on_error(e)
#                     ,
#                     expire)

#                 left_values = left_map.getValues()
#                 for left_value in left_values:
#                     left_values.on_next(value)
                
#             group.add(right.subscribe(on_next
#                 function (e) {
#                     left_values = left_map.getValues()
#                     for (i = 0, len = left_values.length i < len i += 1) {
#                         left_values[i].on_error(e)
                    
#                     observer.on_error(e)
#                 )
#             return r
#         )
#         return AnonymousObservable(subscribe)

#     /**
#      *  Projects each element of an observable sequence into zero or more buffers.
#      *  
#      *  @param {Mixed bufferOpeningsOrClosingSelector Observable sequence whose elements denote the creation of windows, or, a function invoked to define the boundaries of the produced windows (a window is started when the previous one is closed, resulting in non-overlapping windows).
#      *  @param {Function [bufferClosingSelector] A function invoked to define the closing of each produced window. If a closing selector function is specified for the first parameter, self parameter is ignored.
#      *  @returns {Observable An observable sequence of windows.    
#      */
#     observableProto.buffer = function (bufferOpeningsOrClosingSelector, bufferClosingSelector):
#         if (arguments.length === 1 and typeof arguments[0] !== 'function') {
#             return observableWindowWithBounaries.call(self, bufferOpeningsOrClosingSelector).selectMany(function (item) {
#                 return item.toArray()
#             )
        
#         return typeof bufferOpeningsOrClosingSelector === 'function' ?
#             observableWindowWithClosingSelector(bufferOpeningsOrClosingSelector).selectMany(function (item) {
#                 return item.toArray()
#             ) :
#             observableWindowWithOpenings(self, bufferOpeningsOrClosingSelector, bufferClosingSelector).selectMany(function (item) {
#                 return item.toArray()
#             )
    
    
#     /**
#      *  Projects each element of an observable sequence into zero or more windows.
#      *  
#      *  @param {Mixed windowOpeningsOrClosingSelector Observable sequence whose elements denote the creation of windows, or, a function invoked to define the boundaries of the produced windows (a window is started when the previous one is closed, resulting in non-overlapping windows).
#      *  @param {Function [windowClosingSelector] A function invoked to define the closing of each produced window. If a closing selector function is specified for the first parameter, self parameter is ignored.
#      *  @returns {Observable An observable sequence of windows.
#      */    
#     observableProto.window = function (windowOpeningsOrClosingSelector, windowClosingSelector) {
#         if (arguments.length === 1 and typeof arguments[0] !== 'function') {
#             return observableWindowWithBounaries.call(self, windowOpeningsOrClosingSelector)
        
#         return typeof windowOpeningsOrClosingSelector === 'function' ?
#             observableWindowWithClosingSelector.call(self, windowOpeningsOrClosingSelector) :
#             observableWindowWithOpenings.call(self, windowOpeningsOrClosingSelector, windowClosingSelector)
    
    
#     function observableWindowWithOpenings(windowOpenings, windowClosingSelector) {
#         return windowOpenings.groupJoin(self, windowClosingSelector, function () {
#             return observableEmpty()
#         , function (_, window) {
#             return window
#         )
    

#     function observableWindowWithBounaries(windowBoundaries) {
#         source = self
#         return AnonymousObservable(function (observer) {
#             window = Subject(), 
#                 d = CompositeDisposable(), 
#                 r = RefCountDisposable(d)

#             observer.on_next(addRef(window, r))

#             d.add(source.subscribe(function (x) {
#                 window.on_next(x)
#             , function (err) {
#                 window.on_error(err)
#                 observer.on_error(err)
#             , function () {
#                 window.on_completed()
#                 observer.on_completed()
#             ))

#             d.add(windowBoundaries.subscribe(function (w) {
#                 window.on_completed()
#                 window = Subject()
#                 observer.on_next(addRef(window, r))
#             , function (err) {
#                 window.on_error(err)
#                 observer.on_error(err)
#             , function () {
#                 window.on_completed()
#                 observer.on_completed()
#             ))

#             return r
#         )
    

#     function observableWindowWithClosingSelector(windowClosingSelector) {
#         source = self
#         return AnonymousObservable(function (observer) {
#             createWindowClose,
#                 m = SerialDisposable(),
#                 d = CompositeDisposable(m),
#                 r = RefCountDisposable(d),
#                 window = Subject()
#             observer.on_next(addRef(window, r))
#             d.add(source.subscribe(function (x) {
#                 window.on_next(x)
#             , function (ex) {
#                 window.on_error(ex)
#                 observer.on_error(ex)
#             , function () {
#                 window.on_completed()
#                 observer.on_completed()
#             ))
#             createWindowClose = function () {
#                 m1, windowClose
#                 try {
#                     windowClose = windowClosingSelector()
#                  catch (exception) {
#                     observer.on_error(exception)
#                     return
                
#                 m1 = SingleAssignmentDisposable()
#                 m.disposable(m1)
#                 m1.disposable(windowClose.take(1).subscribe(noop, function (ex) {
#                     window.on_error(ex)
#                     observer.on_error(ex)
#                 , function () {
#                     window.on_completed()
#                     window = Subject()
#                     observer.on_next(addRef(window, r))
#                     createWindowClose()
#                 ))
            
#             createWindowClose()
#             return r
#         )
    

#     return Rx
# ))