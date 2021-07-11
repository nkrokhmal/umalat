from app.imports.runtime import *

from app.scheduler.time import *


def make_steam_blocks(block, x=None):
    x = x or block.x
    maker, make = utils.init_block_maker("steam_consumption_blocks", font_size=8, x=x)

    for j in range(block.size[0]):
        make(
            x=(j, 0),
            size=(1, 1),
            text=str(block.props["value"]),
            text_rotation=90,
            push_func=utils.add_push,
        )
    return maker.root


def init_schedule_workbook(wb=None):
    if not wb:
        wb = utils.init_workbook(["Расписание"])

    if "Расписание" not in wb.sheetnames:
        wb.create_sheet("Расписание")

    for ws in wb.worksheets:
        ws.sheet_view.zoomScale = 55

    for i in range(4):
        wb.worksheets[0].column_dimensions[utils.get_column_letter(i + 1)].width = 21
    for i in range(4, 288 * 2):
        wb.worksheets[0].column_dimensions[utils.get_column_letter(i + 1)].width = 2.4
    for i in range(1, 220):
        wb.worksheets[0].row_dimensions[i].height = 25
    return wb


def draw_schedule(schedule, style, O=None, fn=None, wb=None, debug=False):
    wb = init_schedule_workbook(wb)
    O = O or [0, 0]  # initial coordinates

    # update styles
    for b in schedule.iter():
        block_style = style.get(b.props["cls"])

        if block_style:
            block_style = {
                k: v(b) if callable(v) else v for k, v in block_style.items()
            }
            b.props.update(**block_style)

    schedule.props.update(index_width=4)

    for b in schedule.iter():
        if b.is_leaf() and b.props.get("visible", True):
            if b.size[0] == 0 or b.size[1] == 0:
                continue

            text = b.props.get("text", "")
            color = utils.cast_color(b.props.get("color", "white"))

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

                try:
                    utils.draw_block(
                        wb.worksheets[0],
                        x1 + O[0],
                        b.x[1] + O[1],
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
                except AttributeError as e:
                    if "'MergedCell' object attribute 'value' is read-only" in str(e):
                        logger.exception("Block conflict during drawing")
                    if not debug:
                        raise
            except:
                logger.error("Failed to draw block", b=b, x=(x1, b.x[1]), size=b.size)
                logger.error("Relative props", props=b.props.relative_props)
                if os.environ.get("ENVIRONMENT") == "runtime":
                    raise
                else:
                    break
    if fn:
        wb.save(fn)

    return wb


def draw_excel_frontend(
    frontend, style, O=None, open_file=False, fn="schedules/schedule.xlsx", wb=None
):
    wb = draw_schedule(frontend, style, O=O, wb=wb)

    if fn:
        fn = utils.SplitFile(fn).get_new()
        utils.makedirs(fn)
        wb.save(fn)

        if open_file:
            utils.open_file_in_os(fn)

    return wb
