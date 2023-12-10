from typing import Optional

from utils_ak.numeric.numeric import custom_round

from app.enum import LineName
from app.scheduler.time_utils import cast_t


def _get_score(boilings: list) -> float:
    if not boilings:
        return 0
    return max(boiling["pouring"]["first"]["termizator"].y[0] for boiling in boilings) - min(
        boiling["pouring"]["first"]["termizator"].x[0] for boiling in boilings
    )


def calc_partial_score(schedule):
    """The lower - the better"""

    all_boilings = schedule["master"]["boiling", True]
    water_boilings = [
        b for b in schedule["master"]["boiling", True] if b.props["boiling_model"].line.name == LineName.WATER
    ]
    salt_boilings = [
        b for b in schedule["master"]["boiling", True] if b.props["boiling_model"].line.name == LineName.SALT
    ]

    boilings_list = [all_boilings, water_boilings, salt_boilings]
    factors = [1, 2, 1]

    return sum([_get_score(boilings) * factor for boilings, factor in zip(boilings_list, factors)]) / sum(factors)
