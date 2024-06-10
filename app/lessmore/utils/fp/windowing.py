from itertools import chain
from typing import Any, Iterable, Optional

from more_itertools import stagger, windowed as _windowed


# todo later: split to separate files [@marklidenberg]


# a slightly more useful windowed implementation with prefix and suffix
def windowed(
    iterable: Iterable,
    n: Optional[int] = None,
    offsets: Optional[list] = None,
    fillvalue: Any = None,
    step: Optional[int] = None,
    add_prefix: bool = False,
    add_suffix: bool = False,
):

    # - Validate arguments

    assert n is not None or offsets is not None

    # - Add prefix and suffix if needed

    chain_values = [iterable]
    if add_prefix:
        chain_values = [[fillvalue] * (n - 1)] + chain_values
    if add_suffix:
        chain_values = chain_values + [[fillvalue] * (n - 1)]
    iterable = chain(*chain_values)

    if offsets:
        return stagger(iterable=iterable, offsets=offsets, fillvalue=fillvalue)
    elif step:
        return _windowed(seq=iterable, n=n, fillvalue=fillvalue, step=step)
    else:
        return _windowed(seq=iterable, n=n, fillvalue=fillvalue)


def pairwise(
    iterable: Iterable,
    fillvalue: Any = None,
    step: Optional[int] = None,
    add_prefix: bool = False,
    add_suffix: bool = False,
):
    return windowed(
        iterable=iterable,
        n=2,
        fillvalue=fillvalue,
        step=step,
        add_prefix=add_prefix,
        add_suffix=add_suffix,
    )


def test():
    assert list(windowed(iterable=[1, 2, 3, 4, 5], n=3)) == [(1, 2, 3), (2, 3, 4), (3, 4, 5)]
    assert list(windowed(iterable=[1, 2, 3, 4, 5, 6], n=3, fillvalue="!", step=2, add_prefix=True)) == [
        ("!", "!", 1),
        (1, 2, 3),
        (3, 4, 5),
        (5, 6, "!"),
    ]
    assert list(windowed(iterable=[1, 2, 3, 4, 5, 6], n=10, fillvalue="!")) == [(1, 2, 3, 4, 5, 6, "!", "!", "!", "!")]
    assert list(windowed(iterable=[1, 2, 3, 4, 5], n=3, offsets=[0, 1, 3])) == [(1, 2, 4), (2, 3, 5)]

    assert list(pairwise(range(5))) == [(0, 1), (1, 2), (2, 3), (3, 4)]


if __name__ == "__main__":
    test()
