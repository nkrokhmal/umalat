from more_itertools import tail, take as head


def test():

    # -- Take and tail: head and tail

    assert head(n=3, iterable=range(10)) == [0, 1, 2]  # list
    assert list(tail(n=3, iterable=range(10))) == [7, 8, 9]  # iterable


if __name__ == "__main__":
    test()
