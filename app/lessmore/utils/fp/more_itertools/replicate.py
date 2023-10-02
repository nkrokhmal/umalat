from itertools import tee as replicate


"""Naming origins: In computer science, the term "tee" is often used to refer to a device or process that takes an input stream and produces multiple identical output streams."""


def test():
    original_iterator = range(3)
    clone1, clone2 = replicate(original_iterator, 2)
    assert list(clone1) == list(clone2) == [0, 1, 2]


if __name__ == "__main__":
    test()
