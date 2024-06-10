from more_itertools import (
    all_equal,
    all_unique,
    exactly_n,
    first_true,
    iequals as iterables_equal,
    ilen as iterable_len,
    is_sorted,
    minmax,
    quantify as count_if,
)


def test():

    # - Summarizing

    # -- Iterable length

    assert iterable_len(x for x in range(1000000) if x % 3 == 0) == 333334

    # -- Exactly n

    assert exactly_n([True, True, False], 2)
    assert exactly_n([0, 1, 2, 3, 4, 5], 3, lambda x: x < 3)

    # -- Is_sorted

    assert is_sorted(["1", "2", "3", "4", "5"], key=int)
    assert not is_sorted([1, 2, 2], strict=True)

    # -- Minmax: min(), max()

    assert minmax([3, 1, 5]) == (1, 5)
    assert minmax([5, 30], key=str) == (30, 5)
    assert minmax([], default=(0, 0)) == (0, 0)

    # -- Iequals: all

    # NOTE: bad naming, better: iterables_equal
    assert iterables_equal("abc", ["a", "b", "c"], ("a", "b", "c"), iter("abc"))
    assert not iterables_equal("abc", "acb")

    # -- All equal

    assert all_equal("aaa")

    # -- All unique

    assert all_unique("ABCb")
    assert not all_unique("ABCb", str.lower)

    # -- First true

    assert first_true(range(10)) == 1
    assert first_true(range(10), pred=lambda x: x > 5) == 6
    assert first_true(range(10), default="missing", pred=lambda x: x > 9) == "missing"

    # -- Quantify: count if

    assert count_if(range(10), pred=lambda x: x % 2 == 0) == 5
