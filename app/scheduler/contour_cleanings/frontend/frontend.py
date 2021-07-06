# fmt: off
from app.scheduler.time import *
from app.scheduler.frontend import *
from app.scheduler.header import wrap_header
from utils_ak.block_tree import *


def wrap_contour(contour, contour_id):
    m = BlockMaker("contour",
                   default_row_width=1,
                   default_col_width=1,
                   # props
                   font_size=9)

    m.row('label', push_func=add_push,
          size=1, x=-1, text=f'Контур {contour_id + 1}', color='yellow')

    for child in contour.iter():
        if not child.is_leaf():
            continue

        child.update_size(size=(child.size[0], 1))
        m.row(m.copy(child, with_props=True), push_func=add_push)
    return m.root


def wrap_frontend(schedule, date=None, start_time="00:00"):
    date = date or datetime.now()

    m = BlockMaker(
        "frontend",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
    )
    m.row("stub", size=0)  # start with 1
    m.block(wrap_header(date=date, start_time=start_time, header='CIP Мойка контура 1-4'))
    for i, contour in enumerate(schedule.children[:4]):
        m.block(wrap_contour(contour, i))
        m.row('stub', size=0)

    m.block(wrap_header(date=date, start_time=start_time, header='CIP Мойка MPINOX'))
    for i, contour in enumerate(schedule.children[4:]):
        m.block(wrap_contour(contour, i))
        m.row('stub', size=0)
    return m.root
