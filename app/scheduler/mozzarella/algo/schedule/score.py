from app.imports.runtime import *
from app.enum import LineName


def calc_score(schedule):
    line_lengths = {}
    for line_name in [LineName.WATER, LineName.SALT]:
        boilings = [
            b
            for b in schedule["master"]["boiling", True]
            if b.props["boiling_model"].line.name == line_name
        ]
        if boilings:
            beg = min(b.x[0] for b in boilings)
            end = max(b.y[0] for b in boilings)
            line_lengths[line_name] = end - beg
        else:
            line_lengths[line_name] = 0
    score = line_lengths[LineName.WATER] + line_lengths[LineName.SALT] / 3
    return utils.custom_round(score, 0.01)
