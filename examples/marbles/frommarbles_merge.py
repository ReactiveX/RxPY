import reactivex
from reactivex import operators as ops

"""
simple example that merges two cold observables.
"""

source0 = reactivex.cold("a-----d---1--------4-|", timespan=0.01)
source1 = reactivex.cold("--b-c-------2---3-|   ", timespan=0.01)

observable = reactivex.merge(source0, source1).pipe(ops.to_iterable())
elements = observable.run()
print("received {}".format(list(elements)))
