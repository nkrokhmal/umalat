import pandas as pd

from more_itertools import mark_ends
from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.iterative import AxisPusher

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.mozzarella.rubber.to_boiling_plan import to_boiling_plan
from app.scheduler.time_utils import cast_t


def make_schedule(
    boiling_plan: BoilingPlanLike,
    start_time: str = "07:00",
) -> dict:
    # - Get boiling plan

    boiling_plan_df = to_boiling_plan(wb_obj=boiling_plan).copy()

    # - Init block maker

    m = BlockMaker("schedule", default_row_width=1, default_col_width=1, axis=0)

    # - Make schedule

    m.row("preparation", size=24)  # 2 hours

    for is_first, is_last, (i, row) in mark_ends(boiling_plan_df.iterrows()):
        with m.block("packing_group", kg=row["kg"], sku=row["sku"]):
            # - Get packing_speed

            packing_speed = 350  # todo later:  [@marklidenberg]

            # - Split 1000 to [350, 350, 300], all packings are 1 hour

            kg = row["kg"]
            n = kg // packing_speed
            kgs = [packing_speed * 1] * n + [kg - packing_speed * n * 1]
            kgs = [kg for kg in kgs if kg > 0]

            packing_times = [round(kg / packing_speed * 12) for kg in kgs]

            for _is_first, _is_last, (i, packing_time) in mark_ends(enumerate(packing_times)):
                m.row(
                    "packing",
                    size=packing_time,
                    kg=kgs[i],
                )

                if not is_last or not _is_last:
                    if len(list(m.root.iter(cls="packing"))) % 2 == 0:
                        m.row(
                            "long_switch",
                            size=2,
                        )
                    else:
                        m.row(
                            "short_switch",
                            size=1,
                        )

        if not is_last:
            m.row(
                "refurbishment",
                size=4,
            )
        else:
            m.row(
                "cleaning",
                size=37,
            )

    # - Update start time

    m.root.props.update(x=(cast_t(start_time), 0))

    # - Return result

    return {"schedule": m.root, "boiling_plan_df": boiling_plan_df}


def test():
    print(
        make_schedule(
            """/Users/marklidenberg/Desktop/2024.04.19 терка мультиголовы/2024-03-08 План по варкам моцарелла.xlsx"""
        )["schedule"]
    )


if __name__ == "__main__":
    test()
