from datetime import datetime

from utils_ak.block_tree import BlockMaker, add_push

from app.scheduler.boiling_plan_like import BoilingPlanLike
from app.scheduler.brynza.make_schedule.make_schedule import make_packing_schedule
from app.scheduler.wrap_header import wrap_header


def wrap_frontend(
    boiling_plan: BoilingPlanLike,
    date=None,
    start_time: str = "07:00",
) -> dict:
    # - Get schedule

    output = make_packing_schedule(
        boiling_plan=boiling_plan,
        start_time=start_time,
    )
    schedule = output["schedule"]

    # - Plot boilings

    date = datetime.now()

    m = BlockMaker(
        "frontend",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
    )
    m.row("stub", size=0)  # start with 1

    m.block(wrap_header(date=date, start_time=start_time, header="График паковки"))

    # make packing line

    _m = BlockMaker(
        "packing_line",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
    )

    for block in schedule.children:
        _m.block(_m.copy(block, with_props=True, size=(block.size[0], 1)), push_func=add_push)
    m.block(_m.root)

    # - Add frontend to output and return

    output["frontend"] = m.root

    return output


def test():
    print(
        wrap_frontend(
            boiling_plan=f"/Users/arsenijkadaner/FileApps/coding_projects/umalat/app/data/static/samples/by_department/milk_project/2023-11-19 План по варкам милкпроджект Новый.xlsx"
        )
    )


if __name__ == "__main__":
    test()
