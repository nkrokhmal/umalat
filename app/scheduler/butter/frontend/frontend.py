# fmt: off
from app.scheduler.time import *
from app.scheduler.frontend import *
from app.scheduler.header import wrap_header
from utils_ak.block_tree import *


def wrap_line(schedule):
    m = BlockMaker("line",
                   default_row_width=1,
                   default_col_width=1,
                   # props
                   font_size=9)

    for child in schedule.iter():
        if not child.is_leaf():
            continue
        child.update_size(size=(child.size[0], 2))

        if child.props['cls'] == 'pasteurization':
            with m.block('pasteurization', x=(child.x[0], 0), push_func=add_push):
                m.block('pasteurization_1', push_func=add_push,
                        size=(child.size[0], 1), x=(0, 0))

                m.block('pasteurization_2', push_func=add_push,
                        size=(child.size[0], 1), x=(0, 1))
        else:
            m.row(m.copy(child, with_props=True), push_func=add_push)
    return m.root


def wrap_frontend(schedule, date=None, start_time="07:00"):
    date = date or datetime.now()

    m = BlockMaker(
        "frontend",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
    )
    m.row("stub", size=0)  # start with 1
    m.block(wrap_header(date=date, start_time=start_time, header="График работы маслоцеха"))
    m.block(wrap_line(schedule))
    return m.root
