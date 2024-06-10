from more_itertools import stagger as _stagger, windowed as _windowed, windowed_complete


def test():

    # - Windowing

    # -- Windowed: Sliding window

    assert list(_windowed([1, 2, 3, 4, 5], n=3)) == [(1, 2, 3), (2, 3, 4), (3, 4, 5)]

    # -- Stagger:

    assert list(_stagger(range(8), offsets=(0, 2, 4))) == [(0, 2, 4), (1, 3, 5), (2, 4, 6), (3, 5, 7)]
    assert list(_stagger([0, 1, 2, 3], longest=True)) == [
        (None, 0, 1),
        (0, 1, 2),
        (1, 2, 3),
        (2, 3, None),
        (3, None, None),
    ]

    # -- Windowed complete

    assert list(windowed_complete(range(7), n=3)) == [
        ((), (0, 1, 2), (3, 4, 5, 6)),
        ((0,), (1, 2, 3), (4, 5, 6)),
        ((0, 1), (2, 3, 4), (5, 6)),
        ((0, 1, 2), (3, 4, 5), (6,)),
        ((0, 1, 2, 3), (4, 5, 6), ()),
    ]


if __name__ == "__main__":
    test()
