def any_falsey(iterable):
    return any(not item for item in iterable)


def test():
    assert any_falsey([None, None, None])
    assert any_falsey(["", None, None, 1])
    assert not any_falsey([])
    assert not any_falsey([1, 2, 3])


if __name__ == "__main__":
    test()
