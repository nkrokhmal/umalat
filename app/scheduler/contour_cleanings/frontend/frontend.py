# fmt: off
from app.scheduler.time import *
from app.scheduler.frontend import *
from app.scheduler.header import wrap_header
from utils_ak.block_tree import *


def wrap_contour(contour):
    m = BlockMaker("contour",
                   default_row_width=1,
                   default_col_width=1,
                   # props
                   font_size=9)

    for child in contour.iter():
        if not child.is_leaf():
            continue

        child.update_size(size=(child.size[0], 2))
        m.row(m.copy(child, with_props=True), push_func=add_push)
    return m.root


def wrap_frontend(contours, date=None, start_time="00:00"):
    date = date or datetime.now()

    m = BlockMaker(
        "frontend",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
    )
    m.row("stub", size=0)  # start with 1
    m.block(wrap_header(date=date, start_time=start_time, header='Контурные мойки'))
    for contour in contours:
        m.block(wrap_contour(contour))
    return m.root
