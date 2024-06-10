from itertools import chain, tee as replicate
from typing import *

from more_itertools import (
    before_and_after as _before_and_after,
    chunked as _chunked,
    chunked_even as _chunked_even,
    consecutive_groups,
    constrained_batches,
    distribute,
    divide,
    grouper as _grouper,
    partition as _partition,
    sliced as _sliced,
    split_after as split_after,
    split_at as split_at,
    split_before as split_before,
    split_into as split_into,
    split_when as split_when,
)


# todo later: unify splits? [@marklidenberg]


def test():

    # - Splits

    # -- Chunked & variations

    assert (
        (
            isinstance(_chunked(range(7), n=3), Iterable),
            list(_chunked(range(7), n=3)),
            list(_sliced(list(range(7)), n=3)),
            list(_chunked_even(range(7), n=3)),
            list(_grouper(range(7), n=3, incomplete="ignore")),
            list(_grouper(range(7), n=3, incomplete="fill", fillvalue="default")),
        )
    ) == (
        True,
        [[0, 1, 2], [3, 4, 5], [6]],
        [[0, 1, 2], [3, 4, 5], [6]],
        [[0, 1, 2], [3, 4], [5, 6]],
        [(0, 1, 2), (3, 4, 5)],
        [(0, 1, 2), (3, 4, 5), (6, "default", "default")],
    )

    # -- Constrained batches

    assert list(
        constrained_batches(
            iterable=[b"12345", b"123", b"12345678", b"1", b"1", b"12", b"1"],
            max_size=10,
        )
    ) == [
        (b"12345", b"123"),
        (b"12345678", b"1", b"1"),
        (b"12", b"1"),
    ]

    # -- Distribute and divide

    assert (
        [list(c) for c in distribute(n=3, iterable=range(7))],  # memory inefficient, uses itertools.tee() inside
        [list(c) for c in divide(n=2, iterable=range(7))],
    ) == (
        [[0, 3, 6], [1, 4], [2, 5]],
        [[0, 1, 2, 3], [4, 5, 6]],
    )

    # -- Splits

    assert list(split_at(iterable="abcdcba", pred=lambda x: x == "b", keep_separator=False)) == [
        ["a"],
        ["c", "d", "c"],
        ["a"],
    ]  # str.split generalization
    assert (
        list(split_before(iterable="OneTwoThree", pred=lambda s: s.isupper())),
        list(split_after(iterable="OneTwoThree", pred=lambda s: s.isupper())),
    ) == (
        [["O", "n", "e"], ["T", "w", "o"], ["T", "h", "r", "e", "e"]],
        [["O"], ["n", "e", "T"], ["w", "o", "T"], ["h", "r", "e", "e"]],
    )
    assert (
        list(split_into(iterable=[1, 2, 3, 4, 5, 6], sizes=[1, 2, 3])),
        list(split_into(iterable=[1, 2, 3, 4, 5, 6, 7, 8, 9, 0], sizes=[2, 3, None])),
    ) == (
        [[1], [2, 3], [4, 5, 6]],
        [[1, 2], [3, 4, 5], [6, 7, 8, 9, 0]],
    )
    assert list(split_when(iterable=[1, 2, 3, 3, 2, 5, 2, 4, 2], pred=lambda x, y: x > y)) == [
        [1, 2, 3, 3],
        [2, 5],
        [2, 4],
        [2],
    ]

    # -- Before and after

    values, remainder = _before_and_after(predicate=lambda value: value != 2, it=range(5))
    assert list(values) == [0, 1] and list(remainder) == [2, 3, 4]

    # -- Partition

    even_items, odd_items = _partition(pred=lambda x: x % 2 != 0, iterable=range(10))
    assert list(even_items), list(odd_items) == (
        [0, 2, 4, 6, 8],
        [1, 3, 5, 7, 9],
    )

    # -- Consecutive groups

    assert [list(values) for values in consecutive_groups([1, 10, 11, 12, 20, 30, 31, 32, 33, 40])] == [
        [1],
        [10, 11, 12],
        [20],
        [30, 31, 32, 33],
        [40],
    ]


if __name__ == "__main__":
    test()
