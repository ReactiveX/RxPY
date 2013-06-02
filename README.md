# The Reactive Extensions for Python 3

...is a set of libraries to compose asynchronous and event-based programs using observable collections and LINQ-style query operators in Python 3. 

The main Rx repository can be found at [CodePlex](http://rx.codeplex.com/).

## About the Reactive Extensions

The Reactive Extensions for Python (Rx) is a set of libraries for composing asynchronous and event-based programs using observable sequences and LINQ-style query operators in Python. Using Rx, developers represent asynchronous data streams with Observables, query asynchronous data streams using LINQ operators, and parameterize the concurrency in the asynchronous data streams using Schedulers. Simply put, Rx = Observables + LINQ + Schedulers.

Whether you are authoring a client-side or server-side application in Python, you have to deal with asynchronous and event-based programming as a matter of course. Although some patterns are emerging such as the Promise pattern, handling exceptions, cancellation, and synchronization is difficult and error-prone.

Using Rx, you can represent multiple asynchronous data streams (that come from diverse sources, e.g., stock quote, tweets, computer events, web service requests, etc.), and subscribe to the event stream using the Observer object. The Observable notifies the subscribed Observer instance whenever an event occurs.

Because observable sequences are data streams, you can query them using standard LINQ query operators implemented by the Observable type. Thus you can filter, project, aggregate, compose and perform time-based operations on multiple events easily by using these static LINQ operators. In addition, there are a number of other reactive stream specific operators that allow powerful queries to be written. Cancellation, exceptions, and synchronization are also handled gracefully by using the methods on the Observable object.

## Install

To install Rx:

`pip install Rx`
