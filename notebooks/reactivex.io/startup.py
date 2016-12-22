# Helpers.
# Run this cell always after kernel restarts. All other cells are autonomous.
from __future__ import print_function
import rx
import time
import inspect
import logging
from random import randint
from rx.testing import marbles

logging.basicConfig(format="%(threadName)s:%(message)s")
log = logging.getLogger("Rx")
log.setLevel(logging.WARNING)

sleep, now = time.sleep, time.time
O = rx.Observable

ts_glob = 0 # global start time
def reset_start_time(show_doc_for=None, title=True, sleep=None):
    'resets global start time and also prints doc strings'
    global ts_glob
    if sleep:
        log('main thread sleeping %ss' % sleep)
        time.sleep(sleep)
    ts_glob, d = time.time(), show_doc_for
    if title:
        if d:
            if title == True:
                title = d.func_name
        header(title)
    if not d:
        return
    # print the function sig and doc if given
    # py2 compatible way:
    deco, fdef = inspect.getsource(d).split('def ', 1)
    fdef = 'def '.join((deco, fdef.split(')', 1)[0])) + '):'
    print ('module %s\n%s\n%s\n%s' % (d.__module__,
                                      fdef.strip(),
                                      ('    ' + (d.__doc__ or 'n.a.').strip()),
                                      '-' * 80))

rst = reset_start_time

def log(*msg):
    s = ' '.join([str(s) for s in msg])
    print ('%s %s %s' % (dt(ts_glob), cur_thread(), s))

def header(msg):
    print ('\n\n%s %s %s\n' % ('=' * 10, msg, '=' * 10))

def rand():
    return randint(100, 999)

def to_int(s):
    return int(s) if s.isdigit() else s

def dt(ts):
    # the time delta of now to given ts (in millis, 1 float)
    return str('%.1f' % ((time.time() - ts) * 1000)).rjust(6)

class ItemGetter:
    'allows to throw an object onto a format string'
    def __init__(self, obj):
        self.obj = obj
    def __getitem__(self, k, d=None):
        return getattr(self.obj, k, d)

class Subscriber:
    def __init__(self, observed_stream, **kw):
        print ('')
        name = kw.get('name', str(hash(self))[-5:])
        log('New subscription (%s) on stream' % str(name).strip(),
             hash(observed_stream))
        self.ts = time.time() # tstart, for dts at events
        # no postifx after name, sometimes it ends with '\n':
        self.name = name

    def _on(self, what, v=''):
        print ('%s %s [%s] %s: %s -> %s' % (
                dt(ts_glob), cur_thread(), what, dt(self.ts), v, self.name))

    def on_next     (self, v): return self._on('next', v)
    def on_error    (self, v): return self._on('err ', v)
    def on_completed(self)   : return self._on('cmpl', 'fin')

def subs(src, **kw):
    # required for e.g. .multicast:
    obs = Subscriber(src, **kw)
    disposable = src.subscribe(obs)
    if kw.pop('return_subscriber', None):
        return disposable, obs
    return disposable


# getting the current thread
import threading
threads = []
def cur_thread():
    def _cur():
        'return a unique number for the current thread'
        n = threading.current_thread().name
        if 'Main' in n:
            return '    M'
        return '%5s' % ('T' + n.rsplit('-', 1)[-1])
    # you could show all running threads via this:
    #threads = ' '.join([t.name for t in threading.enumerate()])
    #return '%s of %s' % (_cur(), threads)
    return _cur()

from rx.concurrency import new_thread_scheduler, timeout_scheduler
from rx.subjects import Subject
from rx.testing import marbles, dump
def marble_stream(s):
    return O.from_marbles(s).to_blocking()

