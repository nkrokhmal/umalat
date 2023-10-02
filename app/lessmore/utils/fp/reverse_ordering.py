from functools import total_ordering


@total_ordering
class reverse_ordering:
    def __init__(self, obj):
        self.obj = obj

    def __eq__(self, other):
        return other.obj == self.obj

    def __lt__(self, other):
        return other.obj < self.obj


def test():
    assert 1 < 2
    assert reverse_ordering(1) > reverse_ordering(2)


if __name__ == "__main__":
    test()
