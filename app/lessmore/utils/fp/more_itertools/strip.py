from more_itertools import strip


def test():
    # -- Strip: generalized string strip

    assert list(
        strip(iterable=(None, False, None, 1, 2, None, 3, False, None), pred=lambda x: x in {None, False, ""}),
    ) == [
        1,
        2,
        None,
        3,
    ]

    # also lstrip and rstrip


if __name__ == "__main__":
    test()
