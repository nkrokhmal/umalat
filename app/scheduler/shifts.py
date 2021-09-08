from app.imports.runtime import *


def split_shifts(a, b):
    s = b - a

    if s / 12 <= 10:
        # working 10 hours or less - one shift
        return [[a, b]]

    s1 = utils.custom_round(s / 2, 12, rounding="ceil")
    s2 = s - s1
    a, b, s1, s2 = map(int, [a, b, s1, s2])  # convert to int
    return [[a, a + s1], [b - s2, b]]


def split_shifts_by_time(a, b, split, min_shift=12):
    a, b, split = map(int, [a, b, split])  # convert to int
    if b - split >= min_shift:
        return [[a, split], [split, b]]
    else:
        return [[a, b]]
