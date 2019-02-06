import rx
from rx import operators as ops

a = rx.cold(' ---a0---a1----------------a2-|    ')
b = rx.cold('    ---b1---b2---|                 ')
c = rx.cold('             ---c1---c2---|        ')
d = rx.cold('                   -----d1---d2---|')
e1 = rx.cold('a--b--------c-----d-------|       ')

observableLookup = {"a": a, "b": b, "c": c, "d": d}

source = e1.pipe(
    ops.flat_map(lambda value: observableLookup[value]),
    ops.do_action(lambda v: print(v)),
    )

source.run()
