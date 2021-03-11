from utils_ak.block_tree import *

from app.schedule_maker.models import *

validator = ClassValidator(window=3)


def validate(b1, b2):
    pass


validator.add("boiling_group", "boiling_group", validate)


def make_schedule(boiling_plan_df):
    maker, make = init_block_maker("schedule")

    boiling_group_dfs = [
        grp for boiling_id, grp in boiling_plan_df.groupby("boiling_id")
    ]
    assert len(boiling_group_dfs) % 2 == 0

    boiling_groups = []

    for i in range(len(boiling_group_dfs) // 2):
        b1, b2 = boiling_group_dfs[i * 2], boiling_group_dfs[i * 2 + 1]
        boiling_groups.append(make_mascarpone_boiling_group(b1, b2))

    print(boiling_groups)

    return maker.root
