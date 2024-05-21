from datetime import datetime

from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.pushers import add_push, push
from utils_ak.code_block import code
from utils_ak.code_block.code import code
from utils_ak.numeric.numeric import custom_round

from app.lessmore.utils.get_repo_path import get_repo_path
from app.scheduler.adygea.make_schedule.make_schedule import make_schedule
from app.scheduler.common.boiling_plan_like import BoilingPlanLike
from app.scheduler.common.time_utils import cast_t, cast_time
from app.scheduler.common.wrap_header import wrap_header


def wrap_boiling(boiling):
    m = BlockMaker(
        "boiling",
        default_row_width=1,
        default_column_width=1,
        # props
        font_size=9,
        axis=1,
        x=(boiling.x[0], 0),
        size=(0, 2),
        boiling_id=boiling.props["boiling_id"],
        boiling_model=boiling.props["boiling_model"],
        group_name=boiling.props["group_name"],
    )

    with m.push("Upper line"):
        m.row("boiling_num", size=1)
        m.row("boiling_name", size=boiling.size[0] - 1)

    with m.push("Lower line"):
        m.row("collecting", size=boiling["collecting"].size[0], font_size=6)
        m.row("coagulation", size=boiling["coagulation"].size[0])
        m.row("pouring_off", size=boiling["pouring_off"].size[0], font_size=6)

    return m.root


def wrap_lunch(block):
    m = BlockMaker(
        block.props["cls"],
        font_size=9,
        axis=1,
        x=(block.x[0], 0),
        size=(block.size[0], 6),
    )
    return m.root


def wrap_preparation(block):
    m = BlockMaker(
        block.props["cls"],
        font_size=9,
        axis=1,
        x=(block.x[0], 0),
        size=(block.size[0], 2),
    )
    return m.root


def wrap_cleaning(block, last_block):
    a = block.x[0]
    b = last_block.y[0]

    m = BlockMaker(
        block.props["cls"],
        font_size=9,
        axis=1,
        # draw from last boiling with cropped size
        x=(b, 0),
        size=(block.size[0] - (b - a), 14),
    )
    return m.root


def wrap_boiling_lines(schedule):
    m = BlockMaker(
        "boiling_lines",
        default_row_width=1,
        default_column_width=1,
        # props
        axis=1,
    )

    with code("init boiling lines"):
        boiling_lines = []
        n_lines = 4
        for i in range(n_lines):
            boiling_lines.append(m.push(f"boiling_line_{i}", size=(0, 3)).push)
            if i <= n_lines - 2:
                m.row("stub", size=0)

    push(boiling_lines[0], wrap_preparation(schedule["preparation"]), push_func=add_push)

    with code("add boilings"):
        for boiling in schedule["boiling", True]:
            push(boiling_lines[boiling.props["boiler_num"]], wrap_boiling(boiling), push_func=add_push)

    with code("add lunches"):
        for pair_num in range(2):
            try:
                block = schedule.find_one(cls="lunch", pair_num=pair_num)
            except:
                continue
            push(boiling_lines[pair_num * 2], wrap_lunch(block), push_func=add_push)

    with code("add cleaning"):
        block = schedule.find_one(cls="cleaning")
        last_block = max([b for b in schedule["boiling", True]], key=lambda b: b.y[0])
        if len(schedule["lunch", True]) > 0:
            last_block = max([last_block, schedule["lunch", True][-1]], key=lambda b: b.y[0])
        push(boiling_lines[0], wrap_cleaning(block, last_block), push_func=add_push)

    return m.root


def wrap_frontend(
    boiling_plan: BoilingPlanLike,
    date=None,
    start_time: str = "07:00",
    first_batch_ids_by_type: dict = {"adygea": 1},
):
    # - Get schedule

    output = make_schedule(
        boiling_plan=boiling_plan,
        start_time=start_time,
        prepare_start_time=cast_time(cast_t(start_time) - 12),
        first_batch_ids_by_type=first_batch_ids_by_type,
    )
    schedule = output["schedule"]

    # - Wrap frontend

    date = date or datetime.now()

    m = BlockMaker(
        "frontend",
        default_row_width=1,
        default_column_width=1,
        # props
        axis=1,
    )
    m.row("stub", size=0)  # start with 1

    with code("Calc start time"):
        # calc start time
        if "preferred_header_time" in schedule.props.all():
            # currently set in app/main/milk_project/schedule.py
            t = cast_t(schedule.props["preferred_header_time"])
        else:
            t = schedule.x[0]

        start_t = int(custom_round(t, 12, "floor"))  # round to last hour
        start_time = cast_time(start_t)

    m.push(wrap_header(date=date, start_time=start_time, header="График работы котлов"))

    with m.push(start_time=start_time, axis=1):
        m.push(wrap_boiling_lines(schedule))

    # - Add frontend to output and return

    output["frontend"] = m.root

    return output


def test():
    print(wrap_frontend(str(get_repo_path() / "app/data/static/samples/by_department/adygea/sample_schedule.xlsx")))


if __name__ == "__main__":
    test()
