from utils_ak.iteration.simple_iterator import iter_pairs


def group_intervals(intervals, split_criteria=None, interval_func=None):
    if not interval_func:
        interval_func = lambda interval: [interval[0], interval[1]]
    groups = []

    intervals = list(sorted(intervals, key=lambda interval: interval_func(interval)[0]))

    cur_group = []
    for prev_interval, cur_interval in iter_pairs(intervals, method="any_prefix"):
        if not cur_group:
            cur_group.append(cur_interval)
            continue

        if split_criteria(cur_group, prev_interval, cur_interval, interval_func):
            groups.append(cur_group)
            cur_group = [cur_interval]
        else:

            # subsequent
            cur_group.append(cur_interval)

    if cur_group:

        # cur_group is initialized and
        groups.append(cur_group)
    return groups


def basic_criteria(max_length=None, split_func=None):
    def _criteria(cur_group, prev_interval, cur_interval, interval_func):
        if interval_func(cur_group[-1])[-1] != interval_func(cur_interval)[0]:
            return True

        if split_func and split_func(prev_interval, cur_interval):
            return True

        if max_length and len(cur_group) == max_length:
            return True

        return False

    return _criteria


def test_group_intervals():
    intervals = [[1, 2], [4, 5], [2, 4], [10, 11]]
    intervals = list(sorted(intervals, key=lambda interval: interval[0]))
    print(group_intervals(intervals, split_criteria=basic_criteria(max_length=2)))
    assert group_intervals(intervals, split_criteria=basic_criteria(max_length=2)) == [
        [[1, 2], [2, 4]],
        [[4, 5]],
        [[10, 11]],
    ]


if __name__ == "__main__":
    test_group_intervals()
