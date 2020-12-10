from openpyxl.styles import Alignment, PatternFill, Font
import openpyxl


class ExcelBlock:
    def __init__(self, sheet, colour='#FFFFFF', font_size=9):
        self.sheet = sheet
        self.colour = colour
        self.font_size = font_size

    def default_colour(self, row, col, set_colour):
        if set_colour:
            self.sheet.cell(row, col).fill = PatternFill("solid", fgColor=self.colour)

    def default_font(self, row, col, set_font):
        if set_font:
            self.sheet.cell(row, col).font = Font(size=self.font_size)

    def cell_value(self, row, col, value, alignment=None, set_colour=True, set_font=True):
        self.sheet.cell(row, col).value = value
        self.default_colour(row, col, set_colour)
        self.default_font(row, col, set_font)
        if alignment is not None:
            self.sheet.cell(row, col).alignment = alignment

    def merge_cells(self, beg_row, end_row, beg_col, end_col, value, alignment=None, set_colour=True, set_font=True):
        self.sheet.merge_cells(start_row=beg_row,
                               end_row=end_row,
                               start_column=beg_col,
                               end_column=end_col)
        self.cell_value(row=beg_row, col=beg_col, value=value, alignment=alignment, set_colour=set_colour, set_font=set_font)
        self.default_colour(beg_row, beg_col, set_colour)
        self.default_font(beg_row, beg_col, set_font)






