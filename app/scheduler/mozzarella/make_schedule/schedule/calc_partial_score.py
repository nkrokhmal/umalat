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

    boilings_list = []
    factors = []
    # todo next: clean up
    # if len(water_boilings) >= 2 and len(salt_boilings) >= 2:
    #     boilings_list.append(water_boilings)
    #     factors.append(2)
    #     boilings_list.append(salt_boilings)
    #     factors.append(1)

    if len(all_boilings) >= 2:
        boilings_list.append(all_boilings)
        factors.append(1000)

    if not boilings_list:
        return 0

    return sum([_get_score(boilings) * factor for boilings, factor in zip(boilings_list, factors)]) / sum(factors)
