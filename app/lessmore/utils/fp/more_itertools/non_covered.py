from more_itertools import *


value_chain  # special case for collapse
flatten  # collapse for one-level only
prepend  # special case for itertools.chain
sample  # same as random.sample, but can be used with infinite iterables
run_length  # "abbcccdddd" <-> [("a", 1), ("b", 2), ("c", 3), ("d", 4)]
countable  # keep track of how many items have been consumed
consumer  # send() to iterator without next(it) beforehand
callback_iter  # turn callback function into iterator
iter_except  # iterate until exception is raised
side_effect  # pre-processing for iterator
time_limited  # time limited generator
numeric_range  # any numeric range
longest_common_prefix  # longest common prefix
locate  # find multiple index
make_decorator  # decorator for wrapping functions, not really iterable solution
SequenceView  # read only view for sequences
consume  # consume iterator without returning anything, for i in range(n): next(it) equivalent
tabulate  # Return an iterator over the results of func(start), func(start + 1), func(start + 2)…
polynomial_from_roots  # Return a polynomial function from a list of roots
sieve  # Yield the primes less than n.
dotproduct, convolve  # math
substrings, substrings_indexes

# -- Redundant itertools solutions

pairwise, triplewise, sliding_window

# - All combinatorics
