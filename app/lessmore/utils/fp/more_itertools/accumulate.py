import functools

from itertools import accumulate

from more_itertools import difference


def test():
    iterable = accumulate([0, 1, 2, 3, 4])  # produces 0, 1, 3, 6, 10
    assert list(difference(iterable)) == [0, 1, 2, 3, 4]

    assert list(difference([1, 2, 6, 24, 120], lambda x, y: x // y)) == [1, 2, 3, 4, 5]

    it = list(accumulate([1, 2, 3], initial=10))  # [10, 11, 13, 16]
    assert list(difference(it, initial=10)) == [1, 2, 3]  # can pass any initial, same result here

    assert functools.reduce(lambda x, y: x + y, [1, 2, 3]) == 6


if __name__ == "__main__":
    test()
