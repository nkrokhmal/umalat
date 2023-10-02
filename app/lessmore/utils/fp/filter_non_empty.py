from itertools import filterfalse


def filter_non_empty(iterable):
    return filter(None, iterable)


def filter_empty(iterable):
    return filterfalse(None, iterable)


def test():
    assert list(filter_non_empty([1, 2, 3, "", 4, 5, None])) == [1, 2, 3, 4, 5]
    assert list(filter_empty([1, 2, 3, None, 4, 5, None])) == [None, None]


if __name__ == "__main__":
    test()
