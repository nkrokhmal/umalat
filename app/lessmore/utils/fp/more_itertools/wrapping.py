from more_itertools import (
    always_iterable as _always_iterable,
    always_reversible as _always_reversible,
    with_iter as _with_iter,
)


def test():

    # - Wrapping

    # -- Always iterable

    # NOTE: bad naming, better: to_iterable

    assert list(_always_iterable([1, 2, 3])) == [1, 2, 3]
    assert list(_always_iterable(1)) == [1]
    assert list(_always_iterable(None)) == []

    # -- Always reversible

    # NOTE: bad naming, better: to_reversible

    assert list(_always_reversible(x for x in range(3))) == [2, 1, 0]

    # -- With-iter: context manager for iterators

    # upper_lines = (line.upper() for line in with_iter(open('foo')))


if __name__ == "__main__":
    test()
