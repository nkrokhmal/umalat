from functools import partial, update_wrapper


def named_partial(func, *args, **kwargs):
    """A partial function that keeps the original function's docstring and name. functools.partial does not do this."""
    partial_func = partial(func, *args, **kwargs)
    update_wrapper(wrapper=partial_func, wrapped=func)
    return partial_func


def test():

    # - Init function

    def func(a, b, c):
        """This is a function."""
        return a + b + c

    # - Test functools.partial behavior

    partial_func = partial(func, 1, 2)
    assert partial_func(3) == 6
    assert not hasattr(partial_func, "__name__")
    assert (
        partial_func.__doc__
        == """partial(func, *args, **keywords) - new function with partial application
    of the given arguments and keywords.
"""
    )

    # - Test named_partial behavior

    named_partial_func = named_partial(func, 1, 2)
    assert named_partial_func(3) == 6
    assert named_partial_func.__name__ == "func"
    assert named_partial_func.__doc__ == "This is a function."


if __name__ == "__main__":
    test()
