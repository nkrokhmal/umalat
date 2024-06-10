from more_itertools import adjacent as mark_neighbors, intersperse as interspersed, mark_ends, padded, replace


def test():

    # - Augmenting

    # -- Intersperse: fill inbetween

    assert list(interspersed("!", [1, 2, 3, 4, 5])) == [1, "!", 2, "!", 3, "!", 4, "!", 5]
    assert list(interspersed(None, [1, 2, 3, 4, 5], n=2)) == [1, 2, None, 3, 4, None, 5]

    # -- Replace: substitute values

    assert list(replace([1, 1, 0, 1, 1, 0, 1, 1], pred=lambda x: x == 0, substitutes=(2, 3))) == [
        1,
        1,
        2,
        3,
        1,
        1,
        2,
        3,
        1,
        1,
    ]

    # -- Padding

    assert list(padded([1, 2, 3], "?", 5)) == [1, 2, 3, "?", "?"]
    assert list(padded([1, 2, 3, 4], n=3, next_multiple=True)) == [1, 2, 3, 4, None, None]

    # -- Mark ends

    assert list(mark_ends("ABC")) == [(True, False, "A"), (False, False, "B"), (False, True, "C")]

    # -- Adjacent: mark neighbors

    assert list(mark_neighbors(lambda x: x == 3, range(6))) == [
        (False, 0),
        (False, 1),
        (True, 2),
        (True, 3),
        (True, 4),
        (False, 5),
    ]

    assert list(mark_neighbors(lambda x: x == 3, range(6), distance=2)) == [
        (False, 0),
        (True, 1),
        (True, 2),
        (True, 3),
        (True, 4),
        (True, 5),
    ]


if __name__ == "__main__":
    test()
