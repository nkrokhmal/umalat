import openpyxl as opx
from openpyxl.styles import Alignment
from openpyxl.styles import PatternFill

from src.color import cast_color
from src.time import cast_t, cast_time
from src.interval import cast_interval


def draw_block(sheet, x, y, w, h, text, colour):
    if not colour:
        colour = cast_color('white') # default white colour
    sheet.merge_cells(start_row=y, start_column=x, end_row=y + h - 1, end_column=x + w - 1)
    merged_cell = sheet.cell(row=y, column=x)
    merged_cell.value = text
    merged_cell.alignment = Alignment(horizontal='center')
    merged_cell.fill = PatternFill("solid", fgColor=colour[1:])


def draw(sheet, block):
    for b in block.iter():
        if not b.children:
            text = b.abs_props.get('text', '')
            color = cast_color(b.abs_props.get('color', 'white'))

            if b.abs_props.get('visible') == False:
                continue

            text = text.format(**b.abs_props)
            text = text.replace('<', '{')
            text = text.replace('>', '}')
            text = eval(f'f{text!r}')

            beg = b.abs_props['t']
            beg -= cast_t(b.abs_props['beg_time'])  # shift of timeline
            beg += b.abs_props['index_width']  # first index columns
            beg += 1  # indexing starts with 1 in excel

            print(b.abs_props['class'], b.abs_props['y'], cast_interval(beg, beg + b.size))
            draw_block(sheet, beg, b.abs_props['y'], b.size, 1, text, color)


def init_sheet():
    from openpyxl.utils import get_column_letter
    work_book = opx.Workbook()
    sheet = work_book.worksheets[0]
    for i in range(288):
        sheet.column_dimensions[get_column_letter(i + 1)].width = 1.2
    return work_book, sheet


def init_template_sheet():
    def move_sheet(wb, from_loc=None, to_loc=None):
        sheets = wb._sheets

        # if no from_loc given, assume last sheet
        if from_loc is None:
            from_loc = len(sheets) - 1

        # if no to_loc given, assume first
        if to_loc is None:
            to_loc = 0

        sheet = sheets.pop(from_loc)
        sheets.insert(to_loc, sheet)

    work_book = opx.load_workbook(r'2020.11.18 schedule_template.xlsx')

    # delete all but last - original
    for sheet in work_book.worksheets[:-1]:
        work_book.remove_sheet(sheet)

    # copy sheet to work with
    sheet = work_book.copy_worksheet(work_book.worksheets[0])
    # put it at the beginning
    move_sheet(work_book, 1, 0)

    return work_book, sheet