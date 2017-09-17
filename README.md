[![Travis Build Status](https://img.shields.io/travis/ReactiveX/RxPY.svg)](https://travis-ci.org/ReactiveX/RxPY)[![Coveralls Coverage Status](https://img.shields.io/coveralls/dbrattli/RxPY.svg)](https://coveralls.io/r/dbrattli/RxPY)[![pypi version](https://img.shields.io/pypi/v/rx.svg)](https://pypi.python.org/pypi/Rx/)

The Reactive Extensions for Python (RxPY)
=========================================

*A library for composing asynchronous and event-based programs using observable collections and LINQ-style query operators in Python*

O'Reilly has published the video *Reactive Python for Data Science* which is available on both the [O'Reilly Store](https://shop.oreilly.com/product/0636920064237.do) as well as [O'Reilly Safari](https://www.safaribooksonline.com/library/view/reactive-python-for/9781491979006). This video teaches RxPY from scratch with applications towards data science, but should be helpful for anyone seeking to learn RxPY and reactive programming.

[![](http://akamaicovers.oreilly.com/images/0636920064237/lrg.jpg)](https://shop.oreilly.com/product/0636920064237.do)

About ReactiveX
-----------------------------

Reactive Extensions for Python (RxPY) is a set of libraries for composing asynchronous and event-based programs using observable sequences and LINQ-style query operators in Python. Using Rx, developers represent asynchronous data streams with Observables, query asynchronous data streams using operators, and parameterize concurrency in data/event streams using Schedulers.

Using Rx, you can represent multiple asynchronous data streams (that come from diverse sources, e.g., stock quote, Tweets, computer events, web service requests, etc.), and subscribe to the event stream using the Observer object. The Observable notifies the subscribed Observer instance whenever an event occurs.You can put various transformations in-between the source Observable and the consuming Observer as well.

Because Observable sequences are data streams, you can query them using standard LINQ-like query operators implemented by the Observable type. Thus you can filter, map, reduce, compose and perform time-based operations on multiple events easily by using these static LINQ operators. In addition, there are a number of other reactive stream specific operators that allow powerful queries to be written. Cancellation, exceptions, and synchronization are also handled gracefully by using the methods on the Observable object.

Install
-------

RxPY runs on [Python](http://www.python.org/) 2.7, 3.4,[PyPy](http://pypy.org/) and [IronPython](https://ironpython.codeplex.com)

To install RxPY:

`pip install rx`

Note that `pip` may be called `pip3` if you are using Python3.

Tutorials
---------

-	[Getting started with RxPY](https://github.com/ReactiveX/RxPY/blob/develop/notebooks/Getting%20Started.ipynb)
-	General Rx/ReactiveX tutorials
	-	[reactivex.io: Introduction](http://reactivex.io/intro.html)
	-	[reactivex.io: Tutorials](http://reactivex.io/tutorials.html)
	-	[reactivex.io: Operators](http://reactivex.io/documentation/operators.html)

# The Basics


An `Observable` is the core type in ReactiveX. It serially pushes items, known as *emissions*, through a series of operators until it finally arrives at an `Observer`, where they are consumed.

Push-based (rather than pull-based) iteration opens up powerful new possibilities to express code and concurrency much more quickly. Because an `Observable` treats events as data and data as events, composing the two together becomes trivial.

There are many ways to create an `Observable` that hands items to an `Observer`. You can use an `Observable.create()` factory and pass it a function that hands items to the `Observer`. The `Observer` implements `on_next()`, `on_completed()`, and `on_error()` functions. The `on_next()` is used to pass items. The `on_completed()` will signal no more items are coming, and the `on_error()` signals an error.

For instance, you can implement an `Observer` with these three methods and simply print these events. Then the `Observable.create()` can leverage a function that passes five strings to the `Observer` by calling those events.

```python
from rx import Observable, Observer


def push_five_strings(observer):
        observer.on_next("Alpha")
        observer.on_next("Beta")
        observer.on_next("Gamma")
        observer.on_next("Delta")
        observer.on_next("Epsilon")
        observer.on_completed()


class PrintObserver(Observer):

    def on_next(self, value):
        print("Received {0}".format(value))

    def on_completed(self):
        print("Done!")

    def on_error(self, error):
        print("Error Occurred: {0}".format(error))

source = Observable.create(push_five_strings)

source.subscribe(PrintObserver())
```

**OUTPUT:**

```
Received Alpha
Received Beta
Received Gamma
Received Delta
Received Epsilon
Done!
```

However, there are many `Observable` factories for common sources of emissions. To simply push five items, we can rid the `Observable.create()` and its backing function, and use `Observable.from_()`. This factory accepts an iterable, iterates each emission as an `on_next()`, and then calls `on_completed()` when iteration is complete. Therefore, we can simply pass it a list of these five Strings to it.

```python
from rx import Observable, Observer


class PrintObserver(Observer):

    def on_next(self, value):
        print("Received {0}".format(value))

    def on_completed(self):
        print("Done!")

    def on_error(self, error):
        print("Error Occurred: {0}".format(error))

source = Observable.from_(["Alpha", "Beta", "Gamma", "Delta", "Epsilon"])

source.subscribe(PrintObserver())
```

Most of the time you will not want to go through the verbosity of implementing your own `Observer`. You can instead pass 1 to 3 lambda arguments to `subscribe()` specifying the `on_next`, `on_complete`, and `on_error` actions.

```python
from rx import Observable

source = Observable.from_(["Alpha", "Beta", "Gamma", "Delta", "Epsilon"])

source.subscribe(on_next=lambda value: print("Received {0}".format(value)),
                 on_completed=lambda: print("Done!"),
                 on_error=lambda error: print("Error Occurred: {0}".format(error))
                 )
```

You do not have to specify all three events types. You can pick and choose which events you want to observe using the named arguments, or simply provide a single lambda for the `on_next`. Typically in production, you will want to provide an `on_error` so errors are explicitly handled by the subscriber.

```python
from rx import Observable

source = Observable.from_(["Alpha", "Beta", "Gamma", "Delta", "Epsilon"])

source.subscribe(lambda value: print("Received {0}".format(value)))
```

**OUTPUT:**

```
Received Alpha
Received Beta
Received Gamma
Received Delta
Received Epsilon
```


### Operators and Chaining

You can also derive new Observables using over 130 operators available in RxPY. Each operator will yield a new `Observable` that transforms emissions from the source in some way. For example, we can `map()` each `String` to its length, then `filter()` for lengths being at least 5. These will yield two separate Observables built off each other.

```python
from rx import Observable

source = Observable.from_(["Alpha", "Beta", "Gamma", "Delta", "Epsilon"])

lengths = source.map(lambda s: len(s))

filtered = lengths.filter(lambda i: i >= 5)

filtered.subscribe(lambda value: print("Received {0}".format(value)))
```

**OUTPUT:**

```
Received 5
Received 5
Received 5
Received 7
```

Typically, you do not want to save Observables into intermediary variables for each operator, unless you want to have multiple subscribers at that point. Instead, you want to strive to inline and create an "Observable chain" of operations. That way your code is readable and tells a story much more easily.

```python
from rx import Observable

Observable.from_(["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]) \
    .map(lambda s: len(s)) \
    .filter(lambda i: i >= 5) \
    .subscribe(lambda value: print("Received {0}".format(value)))
```

### Emitting Events


On top of data, Observables can also emit events. By treating data and events the same way, you can do powerful compositions to make the two work together. Below, we have an `Observable` that emits a consecutive integer every 1000 milliseconds. This `Observable` will run infinitely and never call `on_complete`.

```python
from rx import Observable

Observable.interval(1000) \
    .map(lambda i: "{0} Mississippi".format(i)) \
    .subscribe(lambda s: print(s))

input("Press any key to quit\n")
```

**OUTPUT:**

```
0 Mississippi
1 Mississippi
2 Mississippi
3 Mississippi
4 Mississippi
5 Mississippi
6 Mississippi
...
```

Because `Observable.interval()` operates on a separate thread (via the `TimeoutScheduler`), we need to prevent the application from exiting prematurely before it has a chance to fire. We can use an `input()` to stop the main thread until a key is pressed. Observables can be created for button events, requests, timers, and even [live Twitter feeds](https://github.com/thomasnield/oreilly_reactive_python_for_data/blob/master/code_examples/8.2_twitter_feed_for_topics.py).

### Multicasting

Each Subscriber to an `Observable` often will receive a separate stream of emissions. For instance, having two subscribers to this `Observable` emitting three random integers will result in both subscribers getting different numbers.

```python
from rx import Observable
from random import randint


three_emissions = Observable.range(1, 3)

three_random_ints = three_emissions.map(lambda i: randint(1, 100000))

three_random_ints.subscribe(lambda i: print("Subscriber 1 Received: {0}".format(i)))
three_random_ints.subscribe(lambda i: print("Subscriber 2 Received: {0}".format(i)))
```

**OUTPUT:**

```
Subscriber 1 Received: 79262
Subscriber 1 Received: 20892
Subscriber 1 Received: 69197
Subscriber 2 Received: 66574
Subscriber 2 Received: 41177
Subscriber 2 Received: 47445
```

To force a specifc point in an `Observable` chain to push the same emissions to all subscribers (rather than generating a separate stream of emissions for each subscriber), you can call `publish()` to return a `ConnectableObservable`. Then you can set up your subscribers and call `connect()` when they are ready to receive the same stream of emissions.

```python
from rx import Observable
from random import randint


three_emissions = Observable.range(1, 3)

three_random_ints = three_emissions.map(lambda i: randint(1, 100000)).publish()

three_random_ints.subscribe(lambda i: print("Subscriber 1 Received: {0}".format(i)))
three_random_ints.subscribe(lambda i: print("Subscriber 2 Received: {0}".format(i)))

three_random_ints.connect()
```

**OUTPUT:**

```
Subscriber 1 Received: 90994
Subscriber 2 Received: 90994
Subscriber 1 Received: 91213
Subscriber 2 Received: 91213
Subscriber 1 Received: 42335
Subscriber 2 Received: 42335
```

This takes a cold `Observable` (which "replays" operations for each subscriber) and makes it hot by putting all Observers on the same stream of emissions which are broadcasted in live time. Be sure to have all your Observers set up before calling `connect()`, as any tardy Observers that subscribe after `connect()` is called will miss any previous emissions.

Another way to implement mutlicasting is to use the `auto_connect()` operator on a `ConnectableObservable`. This will start firing emissions the moment it gets a subscriber, and will continue to fire even as subscribers come and go. If you provide an integer argument, it will hold off firing until there are that many subscribers subscribed to it. 

```python
from rx import Observable
from random import randint


three_emissions = Observable.range(1, 3)

three_random_ints = three_emissions.map(lambda i: randint(1, 100000)).publish().auto_connect(2)

three_random_ints.subscribe(lambda i: print("Subscriber 1 Received: {0}".format(i)))
three_random_ints.subscribe(lambda i: print("Subscriber 2 Received: {0}".format(i))) # second subscriber triggers firing

```

### Combining Observables


You can compose different Observables together using factories like `Observable.merge()`, `Observable.concat()`, `Observable.zip()`, and `Observable.combine_latest()`. Even if Observables are working on different threads (using the `subscribe_on()` and `observe_on()` operators), they will be combined safely. For instance, we can use `Observable.zip()` to slow down emitting 5 Strings by zipping them with an `Observable.interval()`. We will take one emission from each source and zip them into a tuple.


```python
from rx import Observable

letters = Observable.from_(["Alpha", "Beta", "Gamma", "Delta", "Epsilon"])

intervals = Observable.interval(1000)

Observable.zip(letters, intervals, lambda s, i: (s, i)) \
    .subscribe(lambda t: print(t))

input("Press any key to quit\n")
```

**OUTPUT:**

```
('Alpha', 0)
('Beta', 1)
('Gamma', 2)
('Delta', 3)
('Epsilon', 4)
```

You can create Observables off of virtually anything, and it is often helpful to create API's and helper functions that return tailored Observables. For instance, you can create an `Observable` off a [SQL query using SQLAlchemy](http://docs.sqlalchemy.org/en/latest/core/tutorial.html#using-textual-sql), and return a `CUSTOMER` table record for a given customer ID. You can also use `flat_map()` to map each emission to an `Observable` and merge their emissions together into a single `Observable`. This allows us to query for three different customers as shown below.

```python
from sqlalchemy import create_engine, text
from rx import Observable

engine = create_engine('sqlite:///rexon_metals.db')
conn = engine.connect()


def customer_for_id(customer_id):
    stmt = text("SELECT * FROM CUSTOMER WHERE CUSTOMER_ID = :id")
    return Observable.from_(conn.execute(stmt, id=customer_id))


# Query customers with IDs 1, 3, and 5
Observable.from_([1, 3, 5]) \
    .flat_map(lambda id: customer_for_id(id)) \
    .subscribe(lambda r: print(r))
```

**OUTPUT:**

```
(1, 'LITE Industrial', 'Southwest', '729 Ravine Way', 'Irving', 'TX', 75014)
(3, 'Re-Barre Construction', 'Southwest', '9043 Windy Dr', 'Irving', 'TX', 75032)
(5, 'Marsh Lane Metal Works', 'Southeast', '9143 Marsh Ln', 'Avondale', 'LA', 79782)
```

### Concurrency


To achieve concurrency, you use two operators: `subscribe_on()` and `observe_on()`. Both need a `Scheduler` which provides a thread for each subscription to do work (see section on Schedulers below). The `ThreadPoolScheduler` is a good choice to create a pool of reusable worker threads.

> Keep in mind Python's [GIL](https://wiki.python.org/moin/GlobalInterpreterLock) has the potential to undermine your concurrency performance, as it prevents multiple threads from accessing the same line of code simultaneously. Libraries like [NumPy](http://www.numpy.org/) can mitigate this for parallel intensive computations as they free the GIL. RxPy may also minimize thread overlap to some degree. Just be sure to test your application with concurrency and ensure there is a performance gain. 

The `subscribe_on()` instructs the source `Observable` at the start of the chain which scheduler to use (and it does not matter where you put this operator). The `observe_on()`, however, will switch to a different `Scheduler` *at that point* in the `Observable` chain, effectively moving an emission from one thread to another. Some `Observable` factories and operators, like `Observable.interval()` and `delay()`, already have a default `Scheduler` and thus will ignore any `subscribe_on()` you specify (although you can pass a `Scheduler` usually as an argument).

Below, we run three different processes concurrently rather than sequentially using `subscribe_on()` as well as an `observe_on()`.

```python
import multiprocessing
import random
import time
from threading import current_thread

from rx import Observable
from rx.concurrency import ThreadPoolScheduler


def intense_calculation(value):
    # sleep for a random short duration between 0.5 to 2.0 seconds to simulate a long-running calculation
    time.sleep(random.randint(5, 20) * .1)
    return value


# calculate number of CPU's, then create a ThreadPoolScheduler with that number of threads
optimal_thread_count = multiprocessing.cpu_count()
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

# Create Process 1
Observable.from_(["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]) \
    .map(lambda s: intense_calculation(s)) \
    .subscribe_on(pool_scheduler) \
    .subscribe(on_next=lambda s: print("PROCESS 1: {0} {1}".format(current_thread().name, s)),
               on_error=lambda e: print(e),
               on_completed=lambda: print("PROCESS 1 done!"))

# Create Process 2
Observable.range(1, 10) \
    .map(lambda s: intense_calculation(s)) \
    .subscribe_on(pool_scheduler) \
    .subscribe(on_next=lambda i: print("PROCESS 2: {0} {1}".format(current_thread().name, i)),
               on_error=lambda e: print(e), on_completed=lambda: print("PROCESS 2 done!"))

# Create Process 3, which is infinite
Observable.interval(1000) \
    .map(lambda i: i * 100) \
    .observe_on(pool_scheduler) \
    .map(lambda s: intense_calculation(s)) \
    .subscribe(on_next=lambda i: print("PROCESS 3: {0} {1}".format(current_thread().name, i)),
               on_error=lambda e: print(e))

input("Press any key to exit\n")
```

**OUTPUT:**

```
Press any key to exit
PROCESS 1: Thread-1 Alpha
PROCESS 2: Thread-2 1
PROCESS 3: Thread-4 0
PROCESS 2: Thread-2 2
PROCESS 1: Thread-1 Beta
PROCESS 3: Thread-7 100
PROCESS 3: Thread-7 200
PROCESS 2: Thread-2 3
PROCESS 1: Thread-1 Gamma
PROCESS 1: Thread-1 Delta
PROCESS 2: Thread-2 4
PROCESS 3: Thread-7 300
...
```

For more in-depth tutorials, check out *Reactive Python for Data Science* which is available on both the [O'Reilly Store](http://shop.oreilly.com/product/0636920064237.do) as well as [O'Reilly Safari](https://www.safaribooksonline.com/library/view/reactive-python-for/9781491979006).

Python Alignment
----------------

Disposables implements a context manager so you may use them in `with` statements.

Observable sequences may be concatenated using `+`, so you can write:

```python
xs = Observable.from_([1,2,3])
ys = Observable.from_([4,5,6])
zs = xs + ys  # Concatenate observables
```

Observable sequences may be repeated using `*=`, so you can write:

```python
xs = Observable.from_([1,2,3])
ys = xs * 4
```

Observable sequences may be sliced using `[start:stop:step]`, so you can write:

```python
xs = Observable.from_([1,2,3,4,5,6])
ys = xs[1:-1]
```

Observable sequences may be turned into an iterator so you can use generator expressions, or iterate over them (uses queueing and blocking).

```python
xs = Observable.from_([1,2,3,4,5,6])
ys = xs.to_blocking()
zs = (x*x for x in ys if x > 3)
for x in zs:
    print(x)
```

Differences from .NET and RxJS
------------------------------

RxPY is a fairly complete implementation of[Rx](http://msdn.microsoft.com/en-us/data/gg577609.aspx) v2.2 with more than [134 query operators](http://reactivex.io/documentation/operators.html), and over [1100 passing unit-tests](https://coveralls.io/github/dbrattli/RxPY). RxPY is mostly a direct port of RxJS, but also borrows a bit from RxNET and RxJava in terms of threading and blocking operators.

RxPY follows [PEP 8](http://legacy.python.org/dev/peps/pep-0008/), so all function and method names are lowercase with words separated by underscores as necessary to improve readability.

Thus .NET code such as:`c#
var group = source.GroupBy(i => i % 3);
`

need to be written with an `_` in Python:`python
group = source.group_by(lambda i: i % 3)
`

With RxPY you should use [named keyword arguments](https://docs.python.org/2/glossary.html) instead of positional arguments when an operator has multiple optional arguments. RxPY will not try to detect which arguments you are giving to the operator (or not).

```python
res = Observable.timer(5000) # Yes
res = Observable.timer(5000, 1000) # Yes
res = Observable.timer(5000, 1000, Scheduler.timeout) # Yes
res = Observable.timer(5000, scheduler=Scheduler.timeout) # Yes, but must name

res = Observable.timer(5000, Scheduler.timeout) # No, this is an error
```

Thus when an operator like `Observable.timer` has multiple optional arguments you should name your arguments. At least the arguments marked as optional.

Schedulers
----------

In RxPY you can choose to run fully asynchronously or you may decide to schedule work and timeouts using threads.

For time and scheduler handing you will need to supply [datetime](https://docs.python.org/2/library/datetime.html) for absolute time values and [timedelta](https://docs.python.org/2/library/datetime.html#timedelta-objects) for relative time. You may also use `int` to represent milliseconds.

RxPY also comes with batteries included, and has a number of Python specific mainloop schedulers to make it easier for you to use RxPY with your favorite Python framework.

-	`ThreadPoolScheduler` to create a fixed sized pool of Schedulers.
-	`NewThreadScheduler` to create a new thread for each subscription
-	`AsyncIOScheduler` for use with [AsyncIO](https://docs.python.org/3/library/asyncio.html). (requires Python 3.4 or [trollius](http://trollius.readthedocs.org/), a port of `asyncio` compatible with Python 2.6-3.5).
-	`EventLetEventScheduler` for use with [Eventlet](http://eventlet.net/).
-	`IOLoopScheduler` for use with [Tornado IOLoop](http://www.tornadoweb.org/en/stable/networking.html). See the[autocomplete](https://github.com/ReactiveX/RxPY/tree/master/examples/autocomplete) and [konamicode](https://github.com/ReactiveX/RxPY/tree/master/examples/konamicode) examples for how to use RxPY with your Tornado application.
-	`GEventScheduler` for use with [GEvent](http://www.gevent.org/). (Python 2.7 only).
-	`TwistedScheduler` for use with [Twisted](https://twistedmatrix.com/).
-	`TkinterScheduler` for use with [Tkinter](https://wiki.python.org/moin/TkInter). See the [timeflies](https://github.com/ReactiveX/RxPY/tree/master/examples/timeflies) example for how to use RxPY with your Tkinter application.
-	`PyGameScheduler` for use with [PyGame](http://www.pygame.org/). See the [chess](https://github.com/ReactiveX/RxPY/tree/master/examples/chess) example for how to use RxPY with your PyGame application.
-	`QtScheduler` for use with [PyQt4](http://www.riverbankcomputing.com/software/pyqt/download),[PyQt5](http://www.riverbankcomputing.com/software/pyqt/download5), and [PySide](https://wiki.qt.io/Category:LanguageBindings::PySide). See the [timeflies](https://github.com/ReactiveX/RxPY/tree/master/examples/timeflies) example for how to use RxPY with your Qt application.
-	`GtkScheduler` for use with [Python GTK+ 3](https://wiki.gnome.org/Projects/PyGObject). See the [timeflies](https://github.com/ReactiveX/RxPY/tree/master/examples/timeflies) example for how to use RxPY with your GTK+ application.
-	`WxScheduler` for use with [wxPython](http://www.wxpython.org). See the [timeflies](https://github.com/ReactiveX/RxPY/tree/master/examples/timeflies) example for how to use RxPY with your wx application.

Contributing
------------

You can contribute by reviewing and sending feedback on code checkins, suggesting and trying out new features as they are implemented, register issues and help us verify fixes as they are checked in, as well as submit code fixes or code contributions of your own.

The main repository is at [ReactiveX/RxPY](https://github.com/ReactiveX/RxPY). There are currently outdated mirrors at [Reactive-Extensions/RxPy](https://github.com/Reactive-Extensions/RxPy/) and [CodePlex](http://rxpy.codeplex.com/). Please register any issues to [ReactiveX/RxPY/issues](https://github.com/ReactiveX/RxPY/issues).

Note that the master branch is for releases only, so please submit any pull requests against the [develop](https://github.com/ReactiveX/RxPY/tree/develop) branch at [ReactiveX/RxPY](https://github.com/ReactiveX/RxPY/tree/develop).

License
-------

Copyright (c) Microsoft Open Technologies, Inc. All rights reserved. Microsoft Open Technologies would like to thank its contributors, a list of whom are at http://rx.codeplex.com/wikipage?title=Contributors.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
