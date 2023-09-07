from more_itertools import sort_together


def test():
    assert sort_together([(3, 1, 2), (0, 1, 0), ("c", "b", "a")], key_list=(1, 2)) == [
        (2, 3, 1),
        (0, 0, 1),
        ("a", "c", "b"),
    ]


if __name__ == "__main__":
    test()
