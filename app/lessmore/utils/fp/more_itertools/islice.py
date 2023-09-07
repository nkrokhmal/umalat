from itertools import count, islice as _islice

from more_itertools import islice_extended as iterable_slice


def test():
    assert list(_islice("ABCDEFG", 2, None)) == ["C", "D", "E", "F", "G"]
    assert list(iterable_slice(map(str, count()))[10:20:2]) == [
        "10",
        "12",
        "14",
        "16",
        "18",
    ]  # islice with slicing syntax


if __name__ == "__main__":
    test()
