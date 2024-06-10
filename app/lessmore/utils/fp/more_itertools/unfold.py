from more_itertools import one as _one, only as _only, strictly_n


# todo later: make one function for one and only: unfold_one( [@marklidenberg]


def test():

    # -- One

    assert _one([1], too_short=ValueError, too_long=ValueError) == 1

    # -- Strictly N

    assert list(strictly_n(iterable=["a", "b", "c", "d"], n=4)) == ["a", "b", "c", "d"]
    assert list(strictly_n(iterable=["a", "b", "c", "d"], n=1, too_long=lambda item_count: print(item_count))) == ["a"]

    # -- Only

    assert _only([], default="missing", too_long=ValueError) == "missing"
    assert _only([1]) == 1


if __name__ == "__main__":
    test()
