from more_itertools import interleave as _interleave, interleave_evenly as _interleave_evenly, roundrobin as _roundrobin


def test():

    # -- Interleave: round-robing

    assert list(_roundrobin([1, 2, 3], [4, 5], [6, 7, 8])) == [1, 4, 6, 2, 5, 7, 3, 8]  # same as interleave_longest
    assert list(_interleave([1, 2, 3], [4, 5], [6, 7, 8])) == [1, 4, 6, 2, 5, 7]  # stop at shortest
    assert list(_interleave_evenly([[1, 2, 3, 4, 5], ["a", "b"]])) == [
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
