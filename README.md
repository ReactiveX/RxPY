# The Reactive Extensions for Python (RxPY) ... #
*...is a set of libraries to compose asynchronous and event-based programs using observable collections and LINQ-style query operators in Python*

The main repository is at [dbrattli/RxPY](https://github.com/dbrattli/RxPY).
There are currently mirrors at
[Reactive-Extensions/RxPy](https://github.com/Reactive-Extensions/RxPy/) and
[CodePlex](http://rxpy.codeplex.com/). Please register any issues to
[dbrattli/RxPY/issues](https://github.com/dbrattli/RxPY/issues), and make sure 
your pull requests is made against the 
[develop](https://github.com/dbrattli/RxPY/tree/develop) branch.

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
project, aggregate, compose and perform time-based operations on multiple events
easily by using these static LINQ operators. In addition, there are a number of
other reactive stream specific operators that allow powerful queries to be
written. Cancellation, exceptions, and synchronization are also handled
gracefully by using the methods on the Observable object.

## Install

To install RxPY:

`pip install rx`

Note that `pip` may be called `pip3` if your're using Python3.

## Contributing ##

You can contribute by reviewing and sending feedback on code checkins,
suggesting and trying out new features as they are implemented, register issues
and help us verify fixes as they are checked in, as well as submit code fixes or
code contributions of your own.

Note that the master branch is for releases only, so please submit any pull
requests against the [develop](https://github.com/dbrattli/RxPY/tree/develop)
branch at [dbrattli/RxPY](https://github.com/dbrattli/RxPY).

## Differences from RxJS and .NET

RxPY follows [PEP 8](http://legacy.python.org/dev/peps/pep-0008/), so all 
function and method names are lowercase with words separated by underscores as 
necessary to improve readability

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
