import reactivex
import reactivex.operators as ops

"""
Use a dictionnary to convert elements declared in the marbles diagram to
the specified values.
"""

lookup0 = {"a": 1, "b": 3, "c": 5}
lookup1 = {"x": 2, "y": 4, "z": 6}
source0 = reactivex.cold("a---b----c----|", timespan=0.01, lookup=lookup0)
source1 = reactivex.cold("---x---y---z--|", timespan=0.01, lookup=lookup1)

observable = reactivex.merge(source0, source1).pipe(ops.to_iterable())
elements = observable.run()
print("received {}".format(list(elements)))
