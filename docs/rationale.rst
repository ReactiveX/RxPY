.. Rationale

Rationale
==========

Reactive Extensions for Python (RxPY) is a set of libraries for composing
asynchronous and event-based programs using observable sequences and pipable
query operators in Python. Using Rx, developers represent asynchronous data
streams with Observables, query asynchronous data streams using operators, and
parameterize concurrency in data/event streams using Schedulers.

Using Rx, you can represent multiple asynchronous data streams (that come from
diverse sources, e.g., stock quote, Tweets, computer events, web service
requests, etc.), and subscribe to the event stream using the Observer object.
The Observable notifies the subscribed Observer instance whenever an event
occurs. You can put various transformations in-between the source Observable and
the consuming Observer as well.

Because Observable sequences are data streams, you can query them using standard
query operators implemented as functions that can be chained with the pipe
operator. Thus you can filter, map, reduce, compose and perform time-based
operations on multiple events easily by using these operators. In
addition, there are a number of other reactive stream specific operators that
allow powerful queries to be written. Cancellation, exceptions, and
synchronization are also handled gracefully by using dedicated operators.
