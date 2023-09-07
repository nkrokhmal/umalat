import functools

from typing import Callable, Union

import pytest


@pytest.mark.skip
def tested(tests: list[Union[str, Callable]]):
    """Decorator to mark a function as tested.

    Parameters
    ----------
    tests : list[Union[str, Callable]]
        List of tests to assign to function.
        If test is a string, it is assumed to be a function name.
        If test is a function, it is assumed to be a test function.

    Returns
    -------
    Callable
        Decorated function.
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.tests = tests
        return wrapper

    return decorator


def test_function():
    @tested(tests=["test_my_function"])
    def my_function():
        return "a"

    def test_my_function():
        assert my_function() == "a"


def test_class():
    class MyClass:
        @tested(
            tests=["test_my_method"]
        )  # in code use direct function name, so that developers could easily jump to test with IDE
        def my_method(self):
            return "a"

    def test_my_method():
        assert MyClass().my_method() == "a"


if __name__ == "__main__":
    test_function()
    test_class()
