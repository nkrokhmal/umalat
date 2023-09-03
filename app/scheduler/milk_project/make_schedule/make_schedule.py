from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.builtin.collection import crop_to_chunks, remove_duplicates
from utils_ak.iteration.simple_iterator import iter_pairs

from lessmore.utils.get_repo_path import get_repo_path

from app.scheduler.milk_project.make_schedule._boilings import make_boiling, make_boiling_sequence
from app.scheduler.milk_project.to_boiling_plan import BoilingPlanLike, to_boiling_plan
from app.scheduler.time_utils import cast_t


def make_schedule(
    boiling_plan: BoilingPlanLike, start_time="07:00", first_batch_ids_by_type: dict = {"milk_project": 1}
) -> dict:
    # - Process boiling plna

    boiling_plan_df = to_boiling_plan(boiling_plan, first_batch_ids_by_type=first_batch_ids_by_type).copy()

    # - Make schedule

    m = BlockMaker("schedule")
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

    return {"schedule": m.root, "boiling_plan": boiling_plan_df}


def test():
    print(
        make_schedule(
            str(
                get_repo_path()
                / "app/data/static/samples/inputs/by_department/milk_project/План по варкам милкпроджект 3.xlsx"
            )
        )
    )


if __name__ == "__main__":
    test()
