def all_falsey(iterable):
    return all(not item for item in iterable)


def test():
    assert all_falsey([None, None, None])
    assert not all_falsey([None, None, None, 1])
    assert all_falsey([])


if __name__ == "__main__":
    test()
