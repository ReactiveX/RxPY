from rx import Observer
from rx.notification import ON, OE, OC

class MyObserver(Observer):
    def on_next(self, value):
        self.has_on_next = value
    
    def on_error(self, err):
        self.has_on_error = err

    def on_completed(self):
        self.has_on_completed = True

def test_to_observer_notification_on_next():
    i = 0;
    def next(n):
        assert(i == 0)
        assert(n.kind == 'N')
        assert(n.value == 42)
        assert(not hasattr(n, "exception"))
        assert(n.has_value)
    
    Observer.from_notifier(next).on_next(42)

def test_to_observer_notification_on_error():
    ex = 'ex'
    i = 0
    def next(n):
        assert(i == 0)
        assert(n.kind == 'E')
        assert(n.exception == ex)
        assert(not n.has_value)
    
    Observer.from_notifier(next).on_error(ex)

def test_to_observer_notification_on_completed():
    i = 0
    def next(n):
        assert(i == 0)
        assert(n.kind == 'C')
        assert(not n.has_value)

    Observer.from_notifier(next).on_completed()

def test_to_notifier_forwards():
    obsn = MyObserver()
    obsn.to_notifier()(ON(42));
    assert(obsn.has_on_next == 42)

    ex = 'ex'
    obse = MyObserver()
    obse.to_notifier()(OE(ex))
    assert(ex == obse.has_on_error)

    obsc = MyObserver()
    obsc.to_notifier()(OC())
    assert(obsc.has_on_completed)

def test_create_on_next():
    next = False
    def on_next(x):
        nonlocal next
        assert(42 == x);
        next = True

    res = Observer(on_next)
    
    res.on_next(42)
    assert(next)
    return res.on_completed()

def test_create_on_next_has_error():
    ex = 'ex'
    next = False
    _e = None

    def on_next(x):
        nonlocal next
        assert(42 == x)
        next = True

    res = Observer(on_next)
    
    res.on_next(42)
    assert(next)
    
    try:
        res.on_error(ex)
        assert(False)
    except Exception as e:
        e_ = e.args[0]

    assert(ex == e_)

# test('Create_On_nextOn_completed', function () {
#     var next = False;
#     var completed = False;
#     var res = Observer.create(function (x) {
#         assert(42, x);
#         return next = True;
#     }, undefined, function () {
#         return completed = True;
#     });

#     res.on_next(42);

#     assert(next);
#     assert(!completed);

#     res.on_completed();

#     assert(completed);
# });

# test('Create_On_nextOn_completed_HasError', function () {
#     var e_;
#     var ex = 'ex';
#     var next = False;
#     var completed = False;
#     var res = Observer.create(function (x) {
#         assert(42, x);
#         next = True;
#     }, undefined, function () {
#         completed = True;
#     });
#     res.on_next(42);
#     assert(next);
#     assert(!completed);
#     try {
#         res.on_error(ex);
#         assert(False);
#     } catch (e) {
#         e_ = e;
#     }
#     assert(ex, e_);
#     assert(!completed);
# });

# test('Create_On_nextOn_error', function () {
#     var ex = 'ex';
#     var next = True;
#     var error = False;
#     var res = Observer.create(function (x) {
#         assert(42, x);
#         next = True;
#     }, function (e) {
#         assert(ex, e);
#         error = True;
#     });

#     res.on_next(42);

#     assert(next);
#     assert(!error);

#     res.on_error(ex);
#     assert(error);
# });

def test_create_on_next_on_error_hit_completed():
    ex = 'ex'
    next = True
    error = False
    
    def on_next(x):
        nonlocal next
        assert(42 == x)
        next = True
    
    def on_error(e):
        nonlocal error
        assert(ex == e)
        error = True

    res = Observer(on_next, on_error)

    res.on_next(42);
    assert(next)
    assert(not error)

    res.on_completed()

    assert(not error)

def test_create_on_next_on_error_on_completed1():
    ex = 'ex'
    next = True
    error = False
    completed = False
    
    def on_next(x):
        nonlocal next
        assert(42 == x)
        next = True
    
    def on_error(e):
        nonlocal error
        assert(ex == e)
        error = True

    def on_completed():
        nonlocal completed
        completed = True

    res = Observer(on_next, on_error, on_completed)

    res.on_next(42)

    assert(next)
    assert(not error)
    assert(not completed)

    res.on_completed()

    assert(completed)
    assert(not error)

# test('Create_On_nextOn_errorOn_completed2', function () {
#     ex = 'ex';
#     next = True;
#     error = False;
#     completed = False;
#     res = Observer.create(function (x) {
#         assert(42, x);
#         next = True;
#     }, function (e) {
#         assert(ex, e);
#         error = True;
#     }, function () {
#         completed = True;
#     });

#     res.on_next(42);

#     assert(next);
#     assert(!error);
#     assert(!completed);

#     res.on_error(ex);
    
#     assert(!completed);
#     assert(error);
# });

# MyObserver = (function () {
#     function on_next (value) {
#         this.hasOn_next = value;
#     }

#     function on_error (err) {
#         this.hasOn_error = err;
#     }

#     function on_completed () {
#         this.hasOn_completed = True;
#     }

#     return function () {
#         obs = new Observer();
#         obs.on_next = on_next.bind(obs);
#         obs.on_error = on_error.bind(obs);
#         obs.on_completed = on_completed.bind(obs);

#         return obs;
#     };
# }());

# test('AsObserver_Hides', function () {
#     obs, res;
#     obs = new MyObserver();
#     res = obs.asObserver();
#     notDeepassert(obs, res);
# });

# test('AsObserver_Forwards', function () {
#     obsn = new MyObserver();
#     obsn.asObserver().on_next(42);
#     assert(obsn.hasOn_next, 42);

#     ex = 'ex';
#     obse = new MyObserver();
#     obse.asObserver().on_error(ex);
#     assert(obse.hasOn_error, ex);

#     obsc = new MyObserver();
#     obsc.asObserver().on_completed();
#     assert(obsc.hasOn_completed);
# });

# test('Observer_Checked_AlreadyTerminated_Completed', function () {
#     m = 0, n = 0;
#     o = Observer.create(function () { 
#         m++; 
#     }, function () {
#         assert(False);
#     }, function () {
#         n++;
#     }).checked();

#     o.on_next(1);
#     o.on_next(2);
#     o.on_completed();

#     raises(function () { o.on_completed(); });
#     raises(function () { on.on_error(new Error('error')); });
#     assert(2, m);
#     assert(1, n);
# });

# test('Observer_Checked_AlreadyTerminated_Error', function () {
#     m = 0, n = 0;
#     o = Observer.create(function () {
#         m++;
#     }, function () { 
#         n++;
#     }, function () {
#         assert(False);
#     }).checked();

#     o.on_next(1);
#     o.on_next(2);
#     o.on_error(new Error('error'));

#     raises(function () { o.on_completed(); });
#     raises(function () { o.on_error(new Error('error')); });

#     assert(2, m);
#     assert(1, n);
# });

def test_observer_checked_reentrant_next():
    n = 0
    def on_next(x):
        nonlocal n
        n += 1

        try:
            o.on_next(9)
        except Exception:
            pass

        try:
            o.on_error(Exception('error'))
        except Exception:
            pass

        try:
            o.on_completed()
        except Exception:
            pass

    def on_error(ex):
        assert(False)
    
    def on_completed():
        assert(False)
    o = Observer(on_next, on_error, on_completed).checked()

    o.on_next(1)
    assert(1 == n)

# test('Observer_Checked_Reentrant_Error', function () {
#     n = 0;
#     o;
#     o = Observer.create(function () {
#         assert(False);
#     }, function () {
#         n++;
#         raises(function () { o.on_next(9); });
#         raises(function () { o.on_error(new Error('error')); });
#         raises(function () { o.on_completed(); });
#     }, function () {
#         assert(False);
#     }).checked();

#     o.on_error(new Error('error'));
#     assert(1, n);
# });

# test('Observer_Checked_Reentrant_Completed', function () {
#     n = 0;
#     o;
#     o = Observer.create(function () {
#         assert(False);
#     }, function () {
#         assert(False);
#     }, function () {
#         n++;
#         raises(function () { o.on_next(9); });
#         raises(function () { o.on_error(new Error('error')); });
#         raises(function () { o.on_completed(); });
#     }).checked();

#     o.on_completed();
#     assert(1, n);
# });
