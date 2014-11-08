import pyb

from rx.subjects import Subject
from rx.concurrency import PyboardScheduler

s = PyboardScheduler()

stream = Subject()
stream.sample(50, scheduler=s).distinct_until_changed().subscribe(pyb.hid)

accel = pyb.Accel()

# Mainloop
while True:
    value = (0, accel.x(), accel.y(), 0)
    stream.on_next(value)
    s.run() # Process timers