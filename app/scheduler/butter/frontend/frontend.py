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
            with m.block('pasteurization', push_func=add_push,
                         x=(child.x[0], 0),
                         boiling_model=child.props['boiling_model']):
                m.block('pasteurization_1', push_func=add_push,
                        size=(child.size[0], 1), x=(0, 0))

                m.block('pasteurization_2', push_func=add_push,
                        size=(child.size[0], 1), x=(0, 1))
        else:
            m.row(m.copy(child, with_props=True), push_func=add_push)
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

    m.block(wrap_header(date=date, start_time=start_time, header="График работы маслоцеха"))
    with m.block(start_time=start_time, axis=1):
        m.block(wrap_line(schedule))
    return m.root
