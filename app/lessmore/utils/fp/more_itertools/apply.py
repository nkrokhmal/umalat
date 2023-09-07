import math

from itertools import compress, filterfalse as _filterfalse, starmap as _starmap

from more_itertools import filter_except as _filter_except, map_except as _map_except, map_if as _map_if


# todo later: generalize starmap to args and kwargs also [@marklidenberg]
# todo later: flat_map? [@marklidenberg]


def test():
    assert list(_starmap(pow, [(2, 5), (3, 2), (10, 3)])) == [32, 9, 1000]
    assert list(_filter_except(int, ["1", "2", "three", "4", None], ValueError, TypeError)) == ["1", "2", "4"]
    assert list(_map_except(int, ["1", "2", "three", "4", None], ValueError, TypeError)) == [1, 2, 4]
    assert list(
        _map_if(
            list(range(-3, 3)),
            pred=lambda x: x >= 0,
            func=lambda x: f"{math.sqrt(x):.2f}",
            func_else=lambda x: None,
        )
    ) == [None, None, None, "0.00", "1.00", "1.41"]

    assert list(compress("ABCDEF", [1, 0, 1, 0, 1, 1])) == ["A", "C", "E", "F"]

    assert list(filter(lambda x: x < 5, [1, 4, 6, 4, 1])) == [1, 4, 4, 1]
    assert list(_filterfalse(lambda x: x < 5, [1, 4, 6, 4, 1])) == [6]


if __name__ == "__main__":
    test()
