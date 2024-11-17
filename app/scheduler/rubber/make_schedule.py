from itertools import chain

from more_itertools import mark_ends
from utils_ak.block_tree.block_maker import BlockMaker

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.common.boiling_plan_like import BoilingPlanLike
from app.scheduler.common.time_utils import cast_t
from app.scheduler.rubber.to_boiling_plan import to_boiling_plan
from more_itertools import pairwise


def make_schedule(
    boiling_plan: BoilingPlanLike,
    start_time: str = "07:00",
) -> dict:
    # - Get boiling plan

    boiling_plan_df = to_boiling_plan(wb_obj=boiling_plan).copy()

    # - Init block maker

    m = BlockMaker(
        "schedule",
        default_row_width=1,
        default_column_width=1,
        axis=0,
    )

    # - Make schedule

    m.push_row("preparation", size=24)  # 2 hours

    for is_first, is_last, ((prev_i, prev_row), (i, row)) in mark_ends(
        pairwise(chain([[None, None]], boiling_plan_df.iterrows()))
    ):
        if not is_first and prev_row is not None:
            if {prev_row["sku"].weight_netto, row["sku"].weight_netto} == {120.0, 150.0}:
                m.push_row(
                    "refurbishment_and_cleaning",
                    size=8,
                )
            else:
                m.push_row(
                    "refurbishment",
                    size=4,
                )

        with m.push("packing_group", kg=row["kg"], sku=row["sku"]):
            # - Get packing_speed

            packing_speed = row["sku"].packing_speed

            # - Split 1000 to [350, 350, 300], all packings are 1 hour

            kg = row["kg"]
            n = kg // packing_speed
            kgs = [packing_speed * 1] * n + [kg - packing_speed * n * 1]
            kgs = [kg for kg in kgs if kg > 0]

            packing_times = [round(kg / packing_speed * 12) for kg in kgs]

            for _is_first, _is_last, (i, packing_time) in mark_ends(enumerate(packing_times)):
                m.push_row(
                    "packing",
                    size=packing_time,
                    kg=kgs[i],
                )

                if not is_last or not _is_last:
                    if len(list(m.root.iter(cls="packing"))) % 2 == 0:
                        m.push_row(
                            "long_switch",
                            size=2,
                        )
                    else:
                        m.push_row(
                            "short_switch",
                            size=1,
                        )

        if is_last:
            m.push_row(
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
            boiling_plan=str(
                get_repo_path() / "app/data/static/samples/by_department/rubber/sample_rubber_schedule.xlsx"
            ),
        )["schedule"]
    )


if __name__ == "__main__":
    test()
