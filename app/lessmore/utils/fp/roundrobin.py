from more_itertools import interleave, interleave_evenly, roundrobin as _roundrobin


# -- Interleave: round-robing


def round_robin(iterables, exhaust=True, evenly=False):
    assert exhaust or (not exhaust and not evenly), "Unsupported mode"

    if exhaust:
        if evenly:
            return interleave_evenly(iterables)
        else:
            return _roundrobin(*iterables)
    else:
        return interleave(*iterables)


def test():
    assert list(round_robin([[1, 2, 3], [4, 5], [6, 7, 8]])) == [1, 4, 6, 2, 5, 7, 3, 8]  # same as interleave_longest
    assert list(round_robin([[1, 2, 3], [4, 5], [6, 7, 8]], exhaust=False)) == [1, 4, 6, 2, 5, 7]  # stop at shortest
    assert list(round_robin([[1, 2, 3, 4, 5], ["a", "b"]], evenly=True)) == [
        1,
        2,
        "a",
        3,
        4,
        "b",
        5,
    ]  # can also specify lengthes of iterables


if __name__ == "__main__":
    test()
