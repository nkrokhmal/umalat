def all_truthy(iterable):
    return all(item for item in iterable)


def test():
    assert not all_truthy([1, None, None])
    assert all_truthy([1, 1, 1, 1])
    assert all_truthy([])


if __name__ == "__main__":
    test()
