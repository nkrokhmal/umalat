from typing import Optional

from utils_ak.numeric.numeric import custom_round

from app.enum import LineName
from app.scheduler.common.time_utils import cast_t


def calc_score(
    schedule,
    start_times: Optional[dict] = None,
):
    """The lower - the better"""
    score = 0
    line_lengths = {}
    for line_name in [LineName.WATER, LineName.SALT]:
        boilings = [b for b in schedule["master"]["boiling", True] if b.props["boiling_model"].line.name == line_name]
        if boilings:
            beg = min(b.x[0] for b in boilings)
            end = max(b.y[0] for b in boilings)
            beg_melting = min(b["melting_and_packing"].x[0] for b in boilings)
            line_lengths[line_name] = end - beg

            # add penalty for time difference from start_times
            if start_times and start_times.get(line_name):
                score += abs(beg_melting - cast_t(start_times[line_name])) / 10
        else:
            line_lengths[line_name] = 0

    score += line_lengths[LineName.WATER] * 3 / 4 + line_lengths[LineName.SALT] / 4

    return custom_round(score, 0.01)
