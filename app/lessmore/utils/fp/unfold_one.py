from more_itertools import one, only


def unfold_one(iterable, default=..., too_short=None, too_long=None):
    assert default == ... or too_short is None, "too_short and default are mutually exclusive"

    if default is not ...:  # todo later: fp, if_else expression is better here [@marklidenberg]
        return only(iterable, too_long=too_long, default=default)
    else:
        return one(iterable, too_short=too_short, too_long=too_long)


def test():
    assert unfold_one([1], default="foo") == 1
    assert unfold_one([], default="foo") == "foo"

    try:
        unfold_one([], too_short=ValueError)
    except ValueError:
        pass

    try:
        unfold_one([1, 2], too_long=ValueError)
    except ValueError:
        pass


if __name__ == "__main__":
    test()
