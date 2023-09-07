from typing import Iterable, Iterator, Literal, Optional, Tuple, Union

from more_itertools import chunked as chunked_from_more_itertools, chunked_even, grouper, ichunked, sliced


def chunked(
    iterable,
    n: int = 2,
    iterable_chunks: bool = False,
    slice: bool = False,
    mode: Literal["incomplete", "fill", "even", "ignore", "strict"] = "incomplete",
    fillvalue=None,
):
    # - Get output

    if iterable_chunks:
        assert mode == "incomplete"
        return ichunked(iterable=iterable, n=n)
    elif slice:
        assert mode in ["incomplete", "strict"]
        return sliced(seq=iterable, n=n, strict=mode == "strict")
    else:
        # - Process even

        if mode == "even":
            return chunked_even(iterable=iterable, n=n)

        # - Process ignores

        elif mode == "ignore":
            return grouper(iterable=iterable, n=n, incomplete="ignore")

        # - Process fill

        elif mode == "fill":
            return grouper(iterable=iterable, n=n, incomplete="fill", fillvalue=fillvalue)

        elif mode in ["incomplete", "strict"]:
            # same as batched(...)
            return chunked_from_more_itertools(iterable=iterable, n=n, strict=mode == "strict")
        else:
            raise ValueError(f"Unknown mode: {mode}")


def test():
    assert (
        (
            isinstance(chunked(range(7), n=3), Iterable),
            list(chunked(range(7), n=3)),
            list(chunked(range(7), n=3, mode="even")),
            list(chunked(range(7), n=3, mode="ignore")),
            list(chunked(range(7), n=3, mode="fill", fillvalue="default")),
        )
    ) == (
        True,
        [[0, 1, 2], [3, 4, 5], [6]],
        [[0, 1, 2], [3, 4], [5, 6]],
        [(0, 1, 2), (3, 4, 5)],
        [(0, 1, 2), (3, 4, 5), (6, "default", "default")],
    )


if __name__ == "__main__":
    test()
