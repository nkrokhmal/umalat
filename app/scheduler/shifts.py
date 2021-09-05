from app.imports.runtime import *


def split_shifts(a, b):
    s = b - a

    if s / 12 <= 10:
        # working 10 hours or less - one shift
        return [[a, b]]

    s1 = utils.custom_round(s / 2, 12, rounding="ceil")
    s2 = s - s1
    a, b, s1, s2 = map(int, [a, b, s1, s2]) # convert to int
    return [[a, a + s1], [b - s2, b]]
