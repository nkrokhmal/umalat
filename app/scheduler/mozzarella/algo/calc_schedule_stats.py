from app.imports.runtime import *
from app.scheduler.time import *


def calc_schedule_stats(schedule):

    # - Init stats

    stats = {}

    # - Calc max_non_full_cleaning_time

    full_cleanings = list(schedule.iter(cls="cleaning", cleaning_type="full"))
    full_cleanings = list(sorted(full_cleanings, key=lambda c: c.x[0]))

    beg = schedule["master"]["boiling", True][0].x[0]

    values = []

    prev_t = beg
    for c in full_cleanings:
        values.append(c.x[0] - prev_t)
        prev_t = c.y[0]
    stats["max_non_full_cleaning_time"] = cast_time(max(values))

    # - Calc total_time

    stats["total_time"] = cast_time(int(schedule.size[0] - schedule["master"]["boiling", True][0].x[0]))

    # _ Return
    return stats
