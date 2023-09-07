from itertools import chain


def test():
    assert list(chain("ABC", "DEF")) == ["A", "B", "C", "D", "E", "F"]


if __name__ == "__main__":
    test()
