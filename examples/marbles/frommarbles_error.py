import rx
from rx import operators as ops

"""
Specify the error to be raised in place of the # symbol.
"""

err = ValueError("I don't like 5!")

src0 = rx.from_marbles('12-----4-----67--|', timespan=0.2)
src1 = rx.from_marbles('----3----5-#      ', timespan=0.2, error=err)

source = rx.merge(src0, src1).pipe(ops.do_action(print))
source.run()
