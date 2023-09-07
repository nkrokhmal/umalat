from more_itertools import first, last, nth, nth_or_last


def test():
    assert first([0, 1, 2, 3]) == 0
    assert first([], "some default") == "some default"
    assert last([0, 1, 2, 3]) == 3
    assert last([], "some default") == "some default"

    assert nth([0, 1, 2, 3], 10, "zebra") == "zebra"

    assert nth_or_last([0, 1, 2, 3], 2) == 2
    assert nth_or_last([0, 1], 2) == 1
    assert nth_or_last([], 0, default="some default") == "some default"  # if iterable is empty


if __name__ == "__main__":
    test()
