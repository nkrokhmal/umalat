import portion


def cast_interval(a, b):
    return portion.openclosed(a, b)


def calc_interval_length(i):
    if i.empty:
        return 0
    return sum([c.upper - c.lower for c in i])


if __name__ == '__main__':
    print(cast_interval(1,2))
    print(calc_interval_length(cast_interval(1, 2)))