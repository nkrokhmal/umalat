from typing import Callable, Iterable

from more_itertools import unzip


def sorted_together(iterables: Iterable, key: Callable = None, reverse: bool = False):
    return unzip(sorted(zip(*iterables), key=key, reverse=reverse))


def test():
    assert [
        list(values)
        for values in sorted_together([(3, 1, 2), (0, 1, 0), ("c", "b", "a")], key=lambda group: (group[1], group[2]))
    ] == [
        [2, 3, 1],
        [0, 0, 1],
        ["a", "c", "b"],
    ]


if __name__ == "__main__":
    test()
