from typing import Optional

from utils_ak.numeric.numeric import custom_round

from app.enum import LineName
from app.scheduler.time_utils import cast_t


def calc_partial_score(schedule):
    """The lower - the better"""
    min_termizator = min(
        boiling["pouring"]["first"]["termizator"].x[0] for boiling in schedule["master"]["boiling", True]
    )
    max_termizator = max(
        boiling["pouring"]["first"]["termizator"].y[0] for boiling in schedule["master"]["boiling", True]
    )
    return max_termizator - min_termizator
