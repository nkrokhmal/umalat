from more_itertools import collapse, flatten


def test():
    assert list(collapse([(1, 2), [[3, 4], [[5], [6]]]])) == [1, 2, 3, 4, 5, 6]
    assert list(collapse([(1, 2), [[3, 4], [[5], [6]]]], levels=1)) == [
        1,
        2,
        [3, 4],
        [[5], [6]],
    ]  # Only one level flattened
    assert list(collapse([(1, 2), [[3, 4], [[5], [6]]]], base_type=tuple)) == [(1, 2), 3, 4, 5, 6]
    assert list(flatten([(1, 2), [[3, 4], [[5], [6]]]])) == [1, 2, [3, 4], [[5], [6]]]


if __name__ == "__main__":
    test()
