from itertools import zip_longest

from more_itertools import UnequalIterablesError, unzip, zip_broadcast, zip_equal, zip_offset


def test():
    # -- Zip Equal

    try:
        list(zip_equal(range(3), iter("abcd")))
        raise Exception("Should not happen")
    except Exception as e:
        assert type(e) == UnequalIterablesError
        assert str(e) == "Iterables have different lengths"

    # -- Zip broadcast

    assert list(zip_broadcast([1, 2, 3], ["a", "b", "c"], "_")) == [(1, "a", "_"), (2, "b", "_"), (3, "c", "_")]

    # -- Unzip

    letters, numbers = unzip(iterable=[("a", 1), ("b", 2), ("c", 3), ("d", 4)])
    assert (list(letters), list(numbers)) == (["a", "b", "c", "d"], [1, 2, 3, 4])

    # -- Zip longest: zip with padding

    assert list(zip_longest("ABCD", "xy", fillvalue="-")) == [("A", "x"), ("B", "y"), ("C", "-"), ("D", "-")]

    # -- Zip with offset

    assert list(zip_offset("0123", "abcdef", offsets=(0, 1))) == [("0", "b"), ("1", "c"), ("2", "d"), ("3", "e")]


if __name__ == "__main__":
    test()
