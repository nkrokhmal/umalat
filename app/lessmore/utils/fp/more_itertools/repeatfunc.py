import operator

from itertools import islice

from more_itertools import iterate as _iterate, repeatfunc as _repeatfunc, take as head


# - Repeat func: f(), f(), f(),

assert head(6, _repeatfunc(operator.add, None, 3, 5)) == [8, 8, 8, 8, 8, 8]
assert list(_repeatfunc(operator.add, 4, 3, 5)) == [8, 8, 8, 8]

# - Iterate: f(f(f...)))

assert list(islice(_iterate(lambda x: 2 * x, 1), 10)) == [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
