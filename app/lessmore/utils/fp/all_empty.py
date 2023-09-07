def all_empty(iterable):
    return all(not item for item in iterable)


def test():
    assert all_empty([None, None, None])
    assert not all_empty([None, None, None, 1])
    assert all_empty([])


if __name__ == "__main__":
    test()
