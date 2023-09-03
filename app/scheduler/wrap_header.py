from utils_ak.block_tree.block_maker import BlockMaker
from utils_ak.time.dt import cast_str

from app.scheduler.parsing_new_utils.parse_time import cast_label_from_time
from app.scheduler.time_utils import cast_t, cast_time


def wrap_header(date, start_time="07:00", header="", period=566):
    m = BlockMaker(
        "header",
        default_row_width=1,
        default_col_width=1,
        # props
        axis=1,
    )

    with m.block("header", size=(0, 1), index_width=2):
        m.row(size=1, text=header)
        m.row(size=1, text=cast_str(date, "%d.%m.%Y"), bold=True)
        for i in range(period):
            cur_time = cast_time(i + cast_t(start_time))
            days, hours, minutes = cur_time.split(":")
            if cur_time[-2:] == "00":
                m.row(
                    size=1,
                    text=cast_label_from_time(cur_time),
                    color=(218, 150, 148),
                    text_rotation=90,
                    font_size=9,
                )
            else:
                m.row(
                    size=1,
                    text=minutes,
                    color=(204, 255, 255),
                    text_rotation=90,
                    font_size=9,
                )
    return m.root["header"]
