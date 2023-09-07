def any_empty(iterable):
    return any(not item for item in iterable)


def test():
    assert any_empty([None, None, None])
    assert any_empty(["", None, None, 1])
    assert not any_empty([])
    assert not any_empty([1, 2, 3])


if __name__ == "__main__":
    test()
