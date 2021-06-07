# fmt: off
from app.scheduler.time import *
from app.scheduler.frontend import *
from app.scheduler.header import wrap_header
from utils_ak.block_tree import *


def wrap_line(schedule):
    m = BlockMaker("line")

    for child in schedule.iter():
        if not child.is_leaf():
            continue
        child.update_size(size=(child.size[0], 2))
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
    m.block(wrap_header(date=date, start_time=start_time, header="График наливов сыворотки"))
    m.block(wrap_line(schedule))
    return m.root
