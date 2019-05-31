import rx
from rx import scheduler as ccy
from rx import operators as ops

source0 = rx.cold('a-----d---1--------4-|', timespan=0.1)
source1 = rx.cold('--b-c-------2---3-|   ', timespan=0.1)

print("to_marbles() is a blocking operator, we need to wait for completion...")
print('expecting  "a-b-c-d---1-2---3--4-|"')
observable = rx.merge(source0, source1).pipe(ops.to_marbles(timespan=0.1))
diagram = observable.run()
print('got        "{}"'.format(diagram))
