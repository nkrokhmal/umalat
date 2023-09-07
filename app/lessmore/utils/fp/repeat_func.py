from typing import *

from more_itertools import repeatfunc as _repeatfunc, take as head

from lessmore.utils.kwargs_to_args import kwargs_to_args


# todo later: better naming? [@marklidenberg]


def _repeat_func(func: Callable, times: Optional[int], kwargs: Any) -> Iterable:
    return _repeatfunc(
        func,
        times,
        *kwargs_to_args(func, kwargs),
    )


def test():
    print(
        head(
            3,
            _repeat_func(
                func=lambda x: x + 1,
                times=None,
                kwargs={"x": 1},
            ),
        )
    )


if __name__ == "__main__":
    test()
