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


def time_diff(a, b):
    if abs(a - b) < 6:
        return 0
    else:
        return ((abs(a - b) / 6) ** 2) * 6 / 6  # last 6 is a normalizer


def calc_partial_score(schedule, start_times: dict):
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

    if len(water_boilings) >= 2 and len(salt_boilings) >= 2:
        boilings_list.append(water_boilings)
        factors.append(2)
        boilings_list.append(salt_boilings)
        factors.append(1)

    if len(all_boilings) >= 2:
        boilings_list.append(all_boilings)
        factors.append(1)

    if not boilings_list:
        return 0

    score = sum([_get_score(boilings) * factor for boilings, factor in zip(boilings_list, factors)]) / sum(factors)

    # - Add penalty for time deviation

    if len(water_boilings) >= 1 and len(salt_boilings) >= 1:
        for line_name, start_time in start_times.items():
            line_boilings = [b for b in all_boilings if b.props["boiling_model"].line.name == line_name]
            if line_boilings:
                first_line_boiling = line_boilings[0]
                score += time_diff(first_line_boiling["melting_and_packing"].x[0], cast_t(start_time))

    return score
