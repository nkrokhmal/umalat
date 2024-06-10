from typing import Callable, Optional


def group_neighbor_intervals(
    intervals: list,
    max_group_size: Optional[int] = None,
    interval_func: Optional[Callable] = None,  # returns [start, end] of interval
    split_func: Optional[Callable] = None,  # condition that can split a neighbor group
):

    # - Preprocess arguments

    interval_func = interval_func or (lambda interval: [interval[0], interval[1]])

    # - Sort intervals by start time

    intervals = list(sorted(intervals, key=lambda interval: interval_func(interval)[0]))

    # - Group intervals

    groups = []
    cur_group = []
    for interval in intervals:
        if not cur_group:
            cur_group.append(interval)
            continue

        if interval_func(cur_group[-1])[-1] == interval_func(interval)[0] and not (split_func and split_func(interval)):

            # subsequent
            cur_group.append(interval)
            if max_group_size and len(cur_group) == max_group_size:
                groups.append(cur_group)
                cur_group = []
        else:

            # gap between
            groups.append(cur_group)
            cur_group = [interval]

    # - Add last group

    if cur_group:
        groups.append(cur_group)

    # - Return

    return groups


def test():
    intervals = [[1, 2], [2, 4], [4, 5], [10, 11]]
    print(group_neighbor_intervals(intervals, max_group_size=2))


if __name__ == "__main__":
    test()
