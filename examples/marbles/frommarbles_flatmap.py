import reactivex
from reactivex import operators as ops

a = reactivex.cold(" ---a0---a1----------------a2-|    ")
b = reactivex.cold("    ---b1---b2---|                 ")
c = reactivex.cold("             ---c1---c2---|        ")
d = reactivex.cold("                   -----d1---d2---|")
e1 = reactivex.cold("a--b--------c-----d-------|       ")

observableLookup = {"a": a, "b": b, "c": c, "d": d}

source = e1.pipe(
    ops.flat_map(lambda value: observableLookup[value]),
    ops.do_action(lambda v: print(v)),
)

source.run()
