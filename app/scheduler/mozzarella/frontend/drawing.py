from utils_ak.color import *
from utils_ak.openpyxl import *
from app.scheduler.time import *


def draw_schedule(schedule, style, fn=None, wb=None):
    # update styles
    for b in schedule.iter():
        block_style = style.get(b.props["cls"])

        if block_style:
            block_style = {
                k: v(b) if callable(v) else v for k, v in block_style.items()
            }
            b.props.update(**block_style)

    schedule.props.update(index_width=4)

    if not wb:
        wb = init_workbook(["Расписание"])

    if "Расписание" not in wb.sheetnames:
        wb.create_sheet("Расписание")

    schedule_sheet = get_sheet_by_name(wb, 'Расписание')

    set_zoom(schedule_sheet, 55)
    set_dimensions(schedule_sheet, 'column', range(1, 5), 21)
    set_dimensions(schedule_sheet, 'column', range(5, 288 * 2), 2.4)
    set_dimensions(schedule_sheet, 'row', range(1, 220), 25)

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
                    border={"border_style": "thin", "color": "000000"},
                    text_rotation=b.props.get("text_rotation"),
                    font_size=font_size,
                    alignment="center",
                )
            except:
                print("Failed to draw block")
                print(b, x1, b.x[1], b.size[0], b.size[1])
                print(b.props.relative_props, b.x, b.y)
                raise

    if fn:
        wb.save(fn)

    return wb
