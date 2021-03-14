from utils_ak.split_file import *
from utils_ak.os import *

from utils_ak.color import *
from utils_ak.openpyxl import *
from app.schedule_maker.time import *

from loguru import logger


def draw_schedule(schedule, style, fn=None):
    # update styles
    for b in schedule.iter():
        block_style = style.get(b.props["cls"])

        if block_style:
            block_style = {
                k: v(b) if callable(v) else v for k, v in block_style.items()
            }
            b.props.update(**block_style)

    schedule.props.update(index_width=4)

    wb = init_workbook(["Расписание"])

    for ws in wb.worksheets:
        ws.sheet_view.zoomScale = 55

    for i in range(4):
        wb.worksheets[0].column_dimensions[get_column_letter(i + 1)].width = 21
    for i in range(4, 288 * 2):
        wb.worksheets[0].column_dimensions[get_column_letter(i + 1)].width = 2.4
    for i in range(1, 220):
        wb.worksheets[0].row_dimensions[i].height = 25

    for b in schedule.iter():
        if b.is_leaf() and b.props.get("visible", True):
            text = b.props.get("text", "")
            color = cast_color(b.props.get("color", "white"))

            try:
                text = text.format(**b.props.all())
                text = text.replace("<", "{")
                text = text.replace(">", "}")
                text = eval(f"f{text!r}")

                # print(b.props['cls'], b.x, b.y)

                x1 = b.x[0]
                if "start_time" in b.props.all():
                    x1 -= cast_t(b.props["start_time"])  # shift of timeline
                x1 += b.props["index_width"]  # first index columns
                x1 += 1  # indexing starts with 1 in excel

                bold = b.props["bold"]
                font_size = b.props.get("font_size", 12)
                # print(b.props['cls'], x1, b.x[1], b.size[0], b.size[1])

                draw_block(
                    wb.worksheets[0],
                    x1,
                    b.x[1],
                    b.size[0],
                    b.size[1],
                    text,
                    color,
                    bold=bold,
                    border=b.props.relative_props.get(
                        "border", {"border_style": "thin", "color": "000000"}
                    ),
                    text_rotation=b.props.get("text_rotation"),
                    font_size=font_size,
                    alignment="center",
                )
            except:
                logger.error("Failed to draw block", b=b, x=(x1, b.x[1]), size=b.size)
                logger.error("Relative props", props=b.props.relative_props)
                raise
    if fn:
        wb.save(fn)

    return wb


def draw_excel_frontend(frontend, style, open_file=False, fn="schedules/schedule.xlsx"):
    wb = draw_schedule(frontend, style)

    if fn:
        sf = SplitFile(fn)
        fn = sf.get_new()

        makedirs(fn)
        wb.save(fn)

        if open_file:
            open_file_in_os(fn)

    return wb
