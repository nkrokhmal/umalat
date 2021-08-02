# fmt: off
from app.scheduler.time import *
from app.scheduler.frontend import *
from app.scheduler.header import wrap_header
from utils_ak.block_tree import *


def wrap_boiling(boiling):
    m = BlockMaker(
        "boiling",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
        x=(boiling.x[0], 0),
        size=(0, 2),
        boiling_id=boiling.props["boiling_id"],
    )

    with m.block("Upper line"):
        m.row("boiling_num", size=1)
        m.row("boiling_name", size=boiling.size[0] - 1)

    with m.block("Lower line"):
        m.row("collecting", size=boiling["collecting"].size[0])
        m.row("coagulation", size=boiling["coagulation"].size[0])
        m.row("pouring_off", size=boiling["pouring_off"].size[0])

    return m.root


def wrap_boiling_lines(schedule):
    m = BlockMaker(
        "boiling_lines",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
    )

    with code("init boiling lines"):
        boiling_lines = []
        n_lines = 4
        for i in range(n_lines):
            boiling_lines.append(m.block(f"boiling_line_{i}", size=(0, 3)).block)
            if i <= n_lines - 2:
                m.row("stub", size=0)

    with code("add boilings"):
        for boiling in schedule["boiling", True]:
            push(boiling_lines[boiling.props['boiler_num']], wrap_boiling(boiling), push_func=add_push)
    return m.root


def wrap_frontend(schedule, date=None):
    date = date or datetime.now()

    m = BlockMaker(
        "frontend",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
    )
    m.row("stub", size=0)  # start with 1

    # calc start time
    start_t = int(utils.custom_round(schedule.x[0], 12, "floor"))  # round to last hour
    start_time = cast_time(start_t)

    m.block(wrap_header(date=date, start_time=start_time, header="График работы котлов"))

    with m.block(start_time=start_time, axis=1):
        m.block(wrap_boiling_lines(schedule))
    return m.root
