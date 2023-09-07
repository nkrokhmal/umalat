from more_itertools import (
    duplicates_everseen as _duplicates_everseen,
    duplicates_justseen as _duplicates_justseen,
    unique_everseen as _unique_everseen,
    unique_in_window as _unique_in_window,
    unique_justseen as _unique_justseen,
    unique_to_each as _unique_to_each,
)


def test():
    assert list(_unique_in_window([0, 1, 0, 2, 3, 0], n=3)) == [0, 1, 2, 3, 0]

    assert list(_duplicates_everseen("112233 321")) == ["1", "2", "3", "3", "2", "1"]
    assert list(_duplicates_justseen("112233 321")) == ["1", "2", "3"]  # serial duplicates
    assert list(_unique_everseen("112233 321")) == ["1", "2", "3", " "]
    assert list(_unique_justseen("112233 321")) == ["1", "2", "3", " ", "3", "2", "1"]  # serial unique

    assert _unique_to_each({"A", "B"}, {"B", "C"}, {"B", "D"}) == [["A"], ["C"], ["D"]]


if __name__ == "__main__":
    test()
