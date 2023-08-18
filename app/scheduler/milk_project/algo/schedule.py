from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.builtin.collection import crop_to_chunks, remove_duplicates
from utils_ak.iteration.simple_iterator import iter_pairs

from app.scheduler.milk_project.algo.boilings import make_boiling, make_boiling_sequence
from app.scheduler.time import cast_t


def make_schedule(boiling_plan_df, start_time="07:00"):
    m = BlockMaker("schedule")
    boiling_plan_df = boiling_plan_df.copy()
    boilings_ids = remove_duplicates(boiling_plan_df["boiling_id"])

    chunks = list(crop_to_chunks(boilings_ids, 3))
    for ids, next_ids in iter_pairs(chunks, method="any_suffix"):
        _df = boiling_plan_df[boiling_plan_df["boiling_id"].isin(ids)]
        boilings = []
        for boiling_id, grp in _df.groupby("boiling_id"):
            boilings.append(make_boiling(grp))
        boiling_sequence = make_boiling_sequence(boilings)
        m.row(boiling_sequence)

        if next_ids:
            m.row("pouring_off", size=1)
    m.root.props.update(x=(cast_t(start_time), 0))
    return m.root
