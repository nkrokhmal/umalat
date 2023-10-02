from collections import defaultdict
from itertools import count

from more_itertools import bucket as _bucket, groupby_transform as groupby_consecutive, map_reduce as _map_reduce


# todo later: generalize bucket and map_reduce to group_by function [@marklidenberg]


def test():
    # - Groupby

    assert _map_reduce(
        iterable="aAAbBBcCC",
        keyfunc=lambda k: k.upper(),
        valuefunc=lambda v: v.lower(),
        reducefunc=lambda g: "".join(g),
    ) == defaultdict(None, {"A": "aaa", "B": "bbb", "C": "ccc"})

    # -- Bucket: memory efficient map_reduce

    # NOTE: bad naming, groupby is better

    b = _bucket(iterable=["b1", "a1", "c1", "a2", "b2", "c2", "b3"], key=lambda x: x[0])
    assert [[key, list(b[key])] for key in b] == [
        ["b", ["b1", "b2", "b3"]],
        ["a", ["a1", "a2"]],
        ["c", ["c1", "c2"]],
    ]

    # validator case: Odd keys only, other will return empty list. If not specify validator, it will return loop infinitely trying to exhaust the iterable
    s = _bucket(
        iterable=count(1, 2),  # Infinite sequence of odd numbers
        key=lambda x: x % 10,  # Bucket by last digit
        validator=lambda x: x in {1, 3, 5, 7, 9},
    )
    assert (2 in s, list(s[2])) == (False, [])

    # -- Groupby (consecutive)

    # NOTE: BAD NAMING, better name: groupby_consecutive

    assert (
        list(
            groupby_consecutive(  # same as itertools.groupby, but with transform.
                iterable="AaaaBBBCCD11222aaa",
                keyfunc=lambda k: k.upper(),
                valuefunc=lambda v: v.lower(),
                reducefunc=lambda g: "".join(g),
            )
        )
    ) == [("A", "aaaa"), ("B", "bbb"), ("C", "cc"), ("D", "d"), ("1", "11"), ("2", "222"), ("A", "aaa")]


if __name__ == "__main__":
    test()
