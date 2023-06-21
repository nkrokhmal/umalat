def smart_shift(s, key=None, start_from=0):
    if start_from > 0:
        return s[:start_from] + smart_shift(s[start_from:], key=key)

    # swap first zero with one. If next element is not zero - repeat for following elements
    key = key or (lambda v: v)

    assert all([key(v) in [0, 1] for v in s])

    if len(s) <= 1:
        return s

    if key(s[0]) == 0:

        # first zero
        return s

    if all(key(v) == 1 for v in s):

        # all ones
        return s

    # - Find last one before zero: 1, 1, 1, 0 -> 2

    last_one_index = -1
    for i in range(len(s)):
        if key(s[i]) == 1:
            last_one_index += 1
        else:
            break

    return (
        s[:last_one_index] + [s[last_one_index + 1], s[last_one_index]] + smart_shift(s[last_one_index + 2 :], key=key)
    )


def test():
    assert smart_shift([1, 1, 0, 1, 1, 0, 1, 0, 1, 0]) == [1, 0, 1, 1, 0, 1, 0, 1, 0, 1]


if __name__ == "__main__":
    test()
