from itertools import cycle, repeat

from more_itertools import count_cycle, repeat_each, repeat_last


def test():
    repeat(10)  # 10, 10, 10, ...
    repeat_last(range(3))  # 0, 1, 2, 2, 2, ...

    assert list(repeat(10, 3)) == [10, 10, 10]

    assert list(repeat_each("ABC", 3)) == ["A", "A", "A", "B", "B", "B", "C", "C", "C"]

    cycle([1, 2, 3])  # 1, 2, 3, 1, 2, 3, ...

    assert list(count_cycle("AB", 3)) == [(0, "A"), (0, "B"), (1, "A"), (1, "B"), (2, "A"), (2, "B")]


if __name__ == "__main__":
    test()
