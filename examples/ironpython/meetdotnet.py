"""This example shows how to use RxPY together with RxNET in IronPython. Two Rx 
frameworks in one small program.
"""
import clr
import sys
import time

# You need to adjust these to your environment
sys.path.append(r".") # Location of rx
sys.path.append(r"Library/Frameworks/Mono.framework/Versions/3.10.0/lib/mono/gac/System.Reactive.Core/2.2.0.0__31bf3856ad364e35/")
sys.path.append(r"/Library/Frameworks/Mono.framework/Versions/3.10.0/lib/mono/gac/System.Reactive.Linq/2.2.0.0__31bf3856ad364e35/")

clr.AddReference("System.Reactive.Core")
clr.AddReference("System.Reactive.Linq")

# Import RxNET
from System.Reactive.Linq import Observable
from System.Reactive import Observer

# Import RxPY
import rx

stream = rx.subjects.Subject()

def on_next(x):
    print "RxPy: %s" % x
stream.subscribe(on_next)

def OnNext(x):
    print "RxNET: %s" % x
    # Send to RxPY
    stream.on_next(x)
obs = Observer.Create[int](OnNext)

xs = Observable.Range(1, 10)
xs.Subscribe(obs)

print "That was a lot of fun!"