from collections import namedtuple

import openpyxl
import pandas as pd

from openpyxl.utils.cell import column_index_from_string

from app.globals import db
from app.models import RicottaBoiling, RicottaSKU
from app.utils.features.openpyxl_wrapper import ExcelBlock


Cell = namedtuple("Cell", "col, col_name")

COLUMNS = {
    "boiling_number": Cell(column_index_from_string("A"), "A"),
    "boiling_type": Cell(column_index_from_string("B"), "B"),
    "output_kg": Cell(column_index_from_string("C"), "C"),
    "name": Cell(column_index_from_string("D"), "D"),
    "kg": Cell(column_index_from_string("E"), "E"),
    "remainings": Cell(column_index_from_string("F"), "F"),
    "total_output": Cell(column_index_from_string("G"), "G"),
    "boiling_count": Cell(column_index_from_string("J"), "J"),
    "delimiter": Cell(column_index_from_string("K"), "K"),
    "delimiter_int": Cell(column_index_from_string("N"), "N"),
    "total_volume": Cell(column_index_from_string("S"), "S"),
}

ROWS = {
    "total_volume": 2,
}


def draw_boiling_names(wb: openpyxl.Workbook) -> None:
    excel_client = ExcelBlock(wb["Типы варок"])
    boiling_names = set(x.to_str() for x in db.session.query(RicottaBoiling).all())
    excel_client.draw_row(1, ["-"])
    row: int = 2
    for boiling_name in boiling_names:
        excel_client.draw_row(row, [boiling_name], set_border=False)
        row += 1


def draw_skus(wb: openpyxl.Workbook, skus: list[RicottaSKU]) -> None:
    excel_client = ExcelBlock(wb["SKU"])
    excel_client.draw_row(1, ["-", "-", "-"], set_border=False)
    row: int = 2

    for group_sku in sorted(skus, key=lambda x: x.name, reverse=False):
        excel_client.draw_row(
            row,
            [group_sku.name, group_sku.made_from_boilings[0].to_str(), group_sku.made_from_boilings[0].output_kg],
            set_border=False,
        )
        row += 1


def draw_boiling_plan(df: pd.DataFrame, wb: openpyxl.Workbook, total_volume: int = 0) -> openpyxl.Workbook:
    row: int = 3
    skus = db.session.query(RicottaSKU).all()

    draw_boiling_names(wb=wb)
    draw_skus(wb=wb, skus=skus)

    excel_client = ExcelBlock(wb["План варок"])
    sku_columns: list[str] = ["name", "kg"]
    empty_columns: list[str] = ["name", "output_kg", "delimiter"]
    boilings_count: int = 0

    for group_id, group in df.groupby("id", sort=False):
        for i, sku in group.iterrows():
            boilings_count = sku["boiling_count"]
            excel_client.colour = sku["sku"].colour[1:]

            excel_client.color_cell(row=row, col=COLUMNS["boiling_type"].col)
            excel_client.color_cell(row=row, col=COLUMNS["output_kg"].col)

            formula = '=IF({1}{0}="-", "", 1 + SUM(INDIRECT(ADDRESS(2,COLUMN({2}{0})) & ":" & ADDRESS(ROW(),COLUMN({2}{0})))))'.format(
                row,
                COLUMNS["delimiter"].col_name,
                COLUMNS["delimiter_int"].col_name,
            )
            excel_client.draw_cell(
                row=row,
                col=COLUMNS["boiling_number"].col,
                value=formula,
                set_border=False,
            )
            excel_client.draw_row(
                row=row,
                values=[sku[key] for key in sku_columns],
                cols=[COLUMNS[key].col for key in sku_columns],
                set_border=False,
            )
            row += 1

        excel_client.colour = "FFFFFF"
        excel_client.draw_row(
            row=row,
            values=["-"] * len(empty_columns),
            cols=[COLUMNS[key].col for key in empty_columns],
            set_border=False,
        )
        excel_client.draw_cell(
            row=row,
            col=COLUMNS["boiling_count"].col,
            value=boilings_count,
            set_border=False,
        )
        row += 1

    excel_client.font_size = 10
    excel_client.draw_cell(
        row=ROWS["total_volume"],
        col=COLUMNS["total_volume"].col,
        value=total_volume,
        set_border=False,
    )

    wb.active = 2
    return wb
