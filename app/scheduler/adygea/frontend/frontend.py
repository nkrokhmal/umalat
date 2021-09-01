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
        font_size=9,
        axis=1,
        x=(boiling.x[0], 0),
        size=(0, 2),
        boiling_id=boiling.props["boiling_id"],
        boiling_model=boiling.props['boiling_model']
    )

    with m.block("Upper line"):
        m.row("boiling_num", size=1)
        m.row("boiling_name", size=boiling.size[0] - 1)

    with m.block("Lower line"):
        m.row("collecting", size=boiling["collecting"].size[0], font_size=6)
        m.row("coagulation", size=boiling["coagulation"].size[0])
        m.row("pouring_off", size=boiling["pouring_off"].size[0], font_size=6)

    return m.root


def wrap_lunch(block):
    m = BlockMaker(
        block.props['cls'],
        font_size=9,
        axis=1,
        x=(block.x[0], 0),
        size=(block.size[0], 6),
    )
    return m.root

def wrap_cleaning(block, last_block):
    a = block.x[0]
    b = last_block.y[0]

    m = BlockMaker(
        block.props['cls'],
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

    with code('add lunches'):
        for pair_num in range(2):
            try:
                block = schedule.find_one(cls='lunch', pair_num=pair_num)
            except:
                continue
            push(boiling_lines[pair_num * 2], wrap_lunch(block), push_func=add_push)

    with code('add cleaning'):
        block = schedule.find_one(cls='cleaning')
        last_block = schedule['boiling', True][-1]
        if len(schedule['lunch', True]) > 0:
            last_block = max([last_block, schedule['lunch', True][-1]], key=lambda b: b.y[0])
        push(boiling_lines[0], wrap_cleaning(block, last_block), push_func=add_push)

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

    with code('Calc start time'):
        # calc start time
        if 'preferred_header_time' in schedule.props.all():
            # currently set in app/main/milk_project/schedule.py
            t = cast_t(schedule.props['preferred_header_time'])
        else:
            t = schedule.x[0]

        start_t = int(utils.custom_round(t, 12, "floor"))  # round to last hour
        start_time = cast_time(start_t)

    m.block(wrap_header(date=date, start_time=start_time, header="График работы котлов"))

    with m.block(start_time=start_time, axis=1):
        m.block(wrap_boiling_lines(schedule))
    return m.root
