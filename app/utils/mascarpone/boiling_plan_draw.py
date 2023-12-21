from dataclasses import dataclass

import openpyxl
import pandas as pd

from openpyxl.utils.cell import column_index_from_string

from app.imports.runtime import *
from app.models import *
from app.utils.features.merge_boiling_utils import CircularList
from app.utils.features.openpyxl_wrapper import ExcelBlock


Cell = collections.namedtuple("Cell", "col, col_name")

COLUMNS = {
    "boiling_number": Cell(column_index_from_string("A"), "A"),
    "line": Cell(column_index_from_string("B"), "B"),
    "boiling_type": Cell(column_index_from_string("C"), "C"),
    "name": Cell(column_index_from_string("D"), "D"),
    "kg": Cell(column_index_from_string("E"), "E"),
    "remainings": Cell(column_index_from_string("G"), "G"),
    "total_output_kg": Cell(column_index_from_string("G"), "G"),
    "total_input_kg": Cell(column_index_from_string("H"), "H"),
    "delimiter": Cell(column_index_from_string("J"), "J"),
    "delimiter_int": Cell(column_index_from_string("M"), "M"),
    "washing": Cell(column_index_from_string("I"), "I"),
}

ROWS = {
    "total_volume": 2,
}

SKU_SHEET_NAME: str = "SKU Маскарпоне"
PLAN_SHEET_NAME: str = "План варок"


def draw_skus(wb: openpyxl.Workbook, skus: list[SKU], sheet_name: str, row_number: int | None = None) -> int:
    excel_client = ExcelBlock(wb[sheet_name])
    if row_number is None:
        excel_client.draw_row(
            1,
            [
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
            ],
            set_border=False,
        )
        row_number = 2

    for sku in sorted(skus, key=lambda x: x.name, reverse=False):
        b: MascarponeBoiling = sku.made_from_boilings[0]
        excel_client.draw_row(
            row_number,
            [sku.name, b.to_str(), b.output_coeff, b.output_constant, b.input_kg, sku.line.name],
            set_border=False,
        )
        row_number += 1

    return row_number


def get_sku_color(sku_name: str, skus: list[SKU]) -> str:
    sku = next((x for x in skus if x.name == sku_name), None)
    return flask.current_app.config["COLORS"]["Default"] if sku is None else sku.colour


def draw_boiling_sheet(
    wb: openpyxl.Workbook, df: pd.DataFrame, skus: list[SKU], sheet_name: str, row: int | None = None
):
    if df.empty:
        return wb, row

    if row is None:
        row = 3

    excel_client = ExcelBlock(wb[sheet_name])
    sku_columns = ["name", "kg", "boiling_type", "line"]
    empty_columns = ["name", "delimiter", "kg"]
    total_input_kg = 0

    for group_id, group in df.groupby("id", sort=False):
        for i, sku in group.iterrows():
            excel_client.colour = sku["sku"].colour[1:]
            total_input_kg = sku["total_input_kg"]

            excel_client.color_cell(row=row, col=COLUMNS["boiling_type"].col)

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
            col=COLUMNS["total_input_kg"].col,
            value=total_input_kg,
            set_border=False,
        )
        excel_client.draw_cell(
            row=row,
            col=COLUMNS["washing"].col,
            value=0,
            set_border=False,
        )
        row += 1

    return wb, row


def draw_boiling_plan(mascarpone_df, cream_cheese_df, cream_df, wb):
    skus: list[SKU] = db.session.query(MascarponeSKU).join(Group).all()

    draw_skus(wb, skus, SKU_SHEET_NAME)

    SkuGroup = collections.namedtuple("SkuGroup", "df, sheet_name, skus")
    row_number = None
    for item in [
        SkuGroup(cream_df, PLAN_SHEET_NAME, skus),
        SkuGroup(mascarpone_df, PLAN_SHEET_NAME, skus),
        SkuGroup(cream_cheese_df, PLAN_SHEET_NAME, skus),
    ]:

        wb, row_number = draw_boiling_sheet(
            wb=wb, df=item.df, sheet_name=item.sheet_name, skus=item.skus, row=row_number
        )

    # for sheet in wb.sheetnames:
    #     wb[sheet].views.sheetView[0].tabSelected = False

    wb.active = 2
    return wb
