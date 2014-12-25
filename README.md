[![Build Status](https://travis-ci.org/ReactiveX/RxPY.svg?branch=master)](https://travis-ci.org/ReactiveX/RxPY)
[![Coverage Status](https://coveralls.io/repos/dbrattli/RxPY/badge.png)](https://coveralls.io/r/dbrattli/RxPY)
[![Downloads](https://pypip.in/download/Rx/badge.svg)](https://pypi.python.org/pypi/Rx/)

# The Reactive Extensions for Python (RxPY) ... #
*...is a library for composing asynchronous and event-based programs using observable collections and LINQ-style query operators in Python*

The main repository is at [ReactiveX/RxPY](https://github.com/ReactiveX/RxPY).
There are currently outdated mirrors at
[Reactive-Extensions/RxPy](https://github.com/Reactive-Extensions/RxPy/) and
[CodePlex](http://rxpy.codeplex.com/). Please register any issues to
[ReactiveX/RxPY/issues](https://github.com/ReactiveX/RxPY/issues), and make sure
your pull requests is made against the
[develop](https://github.com/ReactiveX/RxPY/tree/develop) branch.

## About the Reactive Extensions

The Reactive Extensions for Python (RxPY) is a set of libraries for composing
asynchronous and event-based programs using observable sequences and LINQ-style
query operators in Python. Using Rx, developers represent asynchronous data
streams with Observables, query asynchronous data streams using LINQ operators,
and parameterize the concurrency in the asynchronous data streams using
Schedulers. Simply put, Rx = Observables + LINQ + Schedulers.

Whether you are authoring a client-side or server-side application in Python,
you have to deal with asynchronous and event-based programming as a matter of
course.

Using Rx, you can represent multiple asynchronous data streams (that come from
diverse sources, e.g., stock quote, tweets, computer events, web service
requests, etc.), and subscribe to the event stream using the Observer object.
The Observable notifies the subscribed Observer instance whenever an event
occurs.

Because observable sequences are data streams, you can query them using standard
LINQ query operators implemented by the Observable type. Thus you can filter,
map, reduce, compose and perform time-based operations on multiple events
easily by using these static LINQ operators. In addition, there are a number of
other reactive stream specific operators that allow powerful queries to be
written. Cancellation, exceptions, and synchronization are also handled
gracefully by using the methods on the Observable object.

## Install

RxPy runs on [Python](http://www.python.org/) 2.7, 3.4,
[PyPy](http://pypy.org/) and [IronPython](https://ironpython.codeplex.com)

To install RxPY:

`pip install rx`

Note that `pip` may be called `pip3` if your're using Python3.

## Differences from .NET and RxJS

RxPY is a fairly complete implementation of
[Rx](http://msdn.microsoft.com/en-us/data/gg577609.aspx)
v2.2 with more than 134 query operators, and over 1100 passing unit-tests. RxPY
is mostly a direct port of RxJS, but also borrows a bit from RxNET and RxJava
in terms of threading and blocking operators.

RxPY follows [PEP 8](http://legacy.python.org/dev/peps/pep-0008/), so all
function and method names are lowercase with words separated by underscores as
necessary to improve readability.

Thus .NET code such as:
```c#
var group = source.GroupBy(i => i % 3);
```

need to be written with an `_` in Python:
```python
group = source.group_by(lambda i: i % 3)
```

With RxPY you should use named
[keyword arguments](https://docs.python.org/2/glossary.html) instead of
positional arguments when an operator has multiple optional arguments. RxPY will
not try to detect which arguments you are giving to the operator (or not).

```python
res = Observable.timer(5000) # Yes
res = Observable.timer(5000, 1000) # Yes
res = Observable.timer(5000, 1000, Scheduler.timeout) # Yes
res = Observable.timer(5000, scheduler=Scheduler.timeout) # Yes, but must name

res = Observable.timer(5000, Scheduler.timeout) # No, this is an error
```

Thus when an operator like `Observable.timeout` has multiple optional arguments
you should name your arguments. At least the arguments marked as optional.

For time and scheduler handing you will need to supply
[datetime](https://docs.python.org/2/library/datetime.html) for absolute time
values and
[timedelta](https://docs.python.org/2/library/datetime.html#timedelta-objects)
for relative time. For relative time values you may also use `int` to represent
milliseconds, or `float` to represent seconds.

RxPY also comes with batteries included, and has a number of Python specific
mainloop schedulers to make it easier for you to use RxPY with your favorite
Python framework.

* `AsyncIOScheduler` for use with
  [AsyncIO](https://docs.python.org/3/library/asyncio.html). (Python 3.4 only).
* `IOLoopScheduler` for use with
  [Tornado IOLoop](http://www.tornadoweb.org/en/stable/networking.html). See the
  [autocomplete](https://github.com/ReactiveX/RxPY/tree/master/examples/autocomplete)
  and [konamicode](https://github.com/ReactiveX/RxPY/tree/master/examples/konamicode)
  examples for howto use RxPY with your Tonado application.
* `GEventScheduler` for use with [GEvent](http://www.gevent.org/).
  (Python 2.7 only).
* `TwistedScheduler` for use with [Twisted](https://twistedmatrix.com/).
* `TkinterScheduler` for use with [Tkinter](https://wiki.python.org/moin/TkInter).
  See the [timeflies](https://github.com/ReactiveX/RxPY/tree/master/examples/timeflies)
  example for howto use RxPY with your Tkinter application.
* `PyGameScheduler` for use with [PyGame](http://www.pygame.org/). See the
  [chess](https://github.com/ReactiveX/RxPY/tree/master/examples/chess)
  example for howto use RxPY with your PyGame application.

## Contributing ##

You can contribute by reviewing and sending feedback on code checkins,
suggesting and trying out new features as they are implemented, register issues
and help us verify fixes as they are checked in, as well as submit code fixes or
code contributions of your own.

Note that the master branch is for releases only, so please submit any pull
requests against the [develop](https://github.com/ReactiveX/RxPY/tree/develop)
branch at [ReactiveX/RxPY](https://github.com/ReactiveX/RxPY).

## License ##

Copyright (c) Microsoft Open Technologies, Inc.  All rights reserved.
Microsoft Open Technologies would like to thank its contributors, a list
of whom are at http://rx.codeplex.com/wikipage?title=Contributors.

Licensed under the Apache License, Version 2.0 (the "License"); you
may not use this file except in compliance with the License. You may
obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing permissions
and limitations under the License.
