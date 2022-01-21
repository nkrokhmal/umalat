

def group_intervals(intervals, split_criteria=None, interval_func=None):
    if not interval_func:
        interval_func = lambda interval: [interval[0], interval[1]]
    groups = []

    intervals = list(sorted(intervals, key=lambda interval: interval_func(interval)[0]))

    cur_group = []
    for interval in intervals:
        if not cur_group:
            cur_group.append(interval)
            continue

        if split_criteria(cur_group, interval, interval_func):
            groups.append(cur_group)
            cur_group = [interval]
        else:
            # subsequent
            cur_group.append(interval)

    if cur_group:
        groups.append(cur_group)
    return groups


def basic_criteria(max_length, split_func=None):
    def _criteria(cur_group, interval, interval_func):
        if interval_func(cur_group[-1])[-1] != interval_func(interval)[0]:
            return True

        if split_func and split_func(interval):
            return True

        if max_length and len(cur_group) == max_length:
            return True

        return False

    return _criteria


def test_group_intervals():
    intervals = [[1, 2], [4, 5], [2, 4], [10, 11]]
    intervals = list(sorted(intervals, key=lambda interval: interval[0]))
    assert group_intervals(intervals, split_criteria=basic_criteria(max_length=2)) == [
        [[1, 2], [2, 4]],
        [[4, 5]],
        [[10, 11]],
    ]

if __name__ == '__main__':
    test_group_intervals()