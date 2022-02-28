import reactivex
from reactivex import scheduler as ccy
from reactivex import operators as ops

source0 = reactivex.cold("a-----d---1--------4-|", timespan=0.1)
source1 = reactivex.cold("--b-c-------2---3-|   ", timespan=0.1)

print("to_marbles() is a blocking operator, we need to wait for completion...")
print('expecting  "a-b-c-d---1-2---3--4-|"')
observable = reactivex.merge(source0, source1).pipe(ops.to_marbles(timespan=0.1))
diagram = observable.run()
print('got        "{}"'.format(diagram))
