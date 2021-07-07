# fmt: off
from app.scheduler.time import *
from app.scheduler.frontend import *
from app.scheduler.header import wrap_header
from utils_ak.block_tree import *


def wrap_line(schedule):
    m = BlockMaker("line",
                   default_row_width=2,
                   default_col_width=2,
                   # props
                   font_size=9)
    for child in schedule.children:
        if child.props['cls'] == 'boiling_sequence':
            for i, block in enumerate(child.children):

                if i == 0:
                    # water collecting
                    _block = m.copy(block, with_props=True)
                    _block.update_size(size=(block.size[0], 2))
                    m.block(_block, push_func=add_push)
                else:
                    for element in block.children:
                        _element = m.copy(element, with_props=True)
                        _element.update_size(size=(element.size[0], 2))
                        _element.props.update(x=(element.x[0], (i - 1) * 2))
                        m.block(_element, push_func=add_push)
        elif child.props['cls'] == 'pouring_off':
            _child = m.copy(child, with_props=True)
            _child.update_size(size=(child.size[0], 6))
            m.block(_child, push_func=add_push)
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

    m.block(wrap_header(date=date, start_time=start_time, header='График работы цеха милкпроджект'))

    with m.block(start_time=start_time, axis=1):
        m.block(wrap_line(schedule))
    return m.root
