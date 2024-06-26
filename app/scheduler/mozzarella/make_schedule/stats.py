from app.scheduler.common.time_utils import cast_time


def calc_schedule_stats(schedule):

    # calc schedule stats
    stats = {}

    # calc full cleaning stats
    full_cleanings = list(schedule.iter(cls="cleaning", cleaning_type="full"))
    full_cleanings = list(sorted(full_cleanings, key=lambda c: c.x[0]))

    beg = schedule["master"]["boiling", True][0].x[0]

    values = []

    prev_t = beg
    for c in full_cleanings:
        values.append(c.x[0] - prev_t)
        prev_t = c.y[0]
    stats["max_non_full_cleaning_time"] = cast_time(max(values))

    stats["total_time"] = cast_time(int(schedule.size[0] - beg))
    return stats
