from more_itertools import peekable as _peekable, seekable as _seekable, spy as _spy


def test():
    # - Lookback and lookahead

    # -- Spy: get head and original iterable

    head, iterable = _spy(range(5))
    assert (head, list(iterable)) == ([0], [0, 1, 2, 3, 4])

    (first_, second), iterable = _spy(range(5), 2)
    assert (first_, second, list(iterable)) == (0, 1, [0, 1, 2, 3, 4])

    # -- Peakable: peek and prepend

    p = _peekable(range(5))
    assert (p.peek(), next(p)) == (0, 0)
    assert bool(p) == True  # non-exhausted

    p = _peekable([])
    assert p.peek(default="hi") == "hi"
    assert bool(p) is False  # exhausted

    p = _peekable(range(5))
    p.prepend(10, 11, 12)
    assert list(p) == [10, 11, 12, 0, 1, 2, 3, 4]

    p = _peekable(range(5))
    assert (p[0], p[2], next(p)) == (0, 2, 0)  # 0, 1, 2 are cached

    # -- Seakable

    it = _seekable(range(5))
    it.seek(2)
    assert list(cache := it.elements()) == [0, 1]
    assert it.peek() == 2  # also peakable
    assert list(cache := it.elements()) == [0, 1, 2]
    it.seek(2)
    assert list(it) == [2, 3, 4]

    # limit cache
    it = _seekable(range(5), maxlen=2)
    it.seek(4)
    assert list(cache := it.elements()) == [2, 3]
