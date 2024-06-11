from datetime import datetime

from utils_ak.block_tree import BlockMaker, add_push

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.brynza.make_schedule.make_schedule import make_packing_schedule
from app.scheduler.common.boiling_plan_like import BoilingPlanLike
from app.scheduler.common.wrap_header import wrap_header


def wrap_frontend(
    boiling_plan: BoilingPlanLike,
    halumi_packings_count: int = 0,
    date=None,
    start_time: str = "07:00",
) -> dict:

    # - Get schedule

    output = make_packing_schedule(
        boiling_plan=boiling_plan,
        halumi_packings_count=halumi_packings_count,
        start_time=start_time,
    )
    schedule = output["schedule"]

    # - Plot boilings

    date = date or datetime.now()

    m = BlockMaker(
        "frontend",
        default_row_width=1,
        default_column_width=1,
        # props
        axis=1,
    )
    m.push_row("stub", size=0)  # start with 1

    m.push(wrap_header(date=date, start_time=start_time, header="График паковки"))

    # make packing line

    _m = BlockMaker(
        "packing_line",
        default_row_width=1,
        default_column_width=1,
        # props
        axis=1,
    )

    for block in schedule.children:
        is_packing = block.props["cls"].startswith("packing_")
        is_packing_brynza = block.props["cls"] == "packing_brynza"
        is_packing_adygea = block.props["cls"] == "packing_adygea"
        is_packing_halumi = block.props["cls"] == "packing_halumi"
        _m.push(
            _m.copy(block, with_props=True, size=(block.size[0], 4 if not is_packing else 2)),
            x=(block.x[0], 0 if not is_packing_brynza and not is_packing_halumi else 2),
            push_func=add_push,
        )

    m.push(_m.root)

    # - Add template

    with m.push("template_block", index_width=1, push_func=add_push):
        m.push(
            "template",
            push_func=add_push,
            x=(1, 2),
            size=(2, 2),
            label="САККАРДО",
        )
        m.push(
            "template",
            push_func=add_push,
            x=(1, 4),
            size=(2, 2),
            label="МУЛЬТИВАК",
        )

    # - Add frontend to output and return

    output["frontend"] = m.root

    return output


def test():
    print(
        wrap_frontend(
            boiling_plan=str(
                get_repo_path()
                / "app/data/static/samples/by_department/milk_project/sample_boiling_plan_milk_project.xlsx"
            ),
            halumi_packings_count=2,
        )
    )


if __name__ == "__main__":
    test()
