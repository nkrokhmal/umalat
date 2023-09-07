from itertools import dropwhile, takewhile


def test():
    # - Takewhile

    assert list(takewhile(lambda x: x < 5, [1, 4, 6, 4, 1])) == [1, 4]

    # - Dropwhile: drop items while predicate is true

    assert list(dropwhile(lambda x: x < 5, [1, 4, 6, 4, 1])) == [6, 4, 1]


if __name__ == "__main__":
    test()
