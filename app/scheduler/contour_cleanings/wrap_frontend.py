from datetime import datetime

from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.block_tree.pushers.pushers import add_push
from utils_ak.code_block import code
from utils_ak.code_block.code import code

from app.scheduler.common.time_utils import cast_t, cast_time, parse_time
from app.scheduler.common.wrap_header import wrap_header


def wrap_contour(contour, contour_id):
    m = BlockMaker(
        "contour",
        default_row_width=1,
        default_column_width=1,
        # props
        font_size=9,
    )

    for child in contour.iter():
        if not child.is_leaf():
            continue

        child.update_size(size=(child.size[0], 1))
        m.push_row(m.copy(child, with_props=True), push_func=add_push)
    return m.root


def wrap_frontend(schedule, date=None):
    date = date or datetime.now()

    with code("Calc start time"):
        min_t = min([block.x[0] for block in schedule.iter(cls="cleaning")])
        days, _, _ = parse_time(min_t)
        start_time = cast_time((days, 0, 0))

    m = BlockMaker(
        "frontend",
        default_row_width=1,
        default_column_width=1,
        # props
        axis=1,
    )
    m.push_row("stub", size=0)  # start with 1
    m.push(wrap_header(date=date, start_time=start_time, header="CIP Мойка контура 1-4"))
    with m.push("contours 1-4", start_time=start_time, axis=1):
        for i, contour in enumerate(schedule.children[:4]):
            m.push(wrap_contour(contour, i))
            m.push(
                "label",
                push_func=add_push,
                size=(1, 1),
                x=(-1 + cast_t(start_time), 2 * i),
                text=f"Контур {i + 1}",
                color="yellow",
            )
            m.push_row("stub", size=0)

    m.push(wrap_header(date=date, start_time=start_time, header="CIP Мойка MPINOX"))
    with m.push("mpinox", start_time=start_time, axis=1):
        for i, contour in enumerate(schedule.children[4:]):
            m.push(wrap_contour(contour, i))
            m.push(
                "label",
                push_func=add_push,
                size=(1, 1),
                x=(-1 + cast_t(start_time), 2 * i),
                text=f"Контур {i + 1}",
                color="yellow",
            )
            m.push_row("stub", size=0)
    return m.root
