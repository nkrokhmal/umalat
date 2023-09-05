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
    "boiling_type": Cell(column_index_from_string("B"), "B"),
    "output": Cell(column_index_from_string("C"), "C"),
    "name": Cell(column_index_from_string("D"), "D"),
    "kg_output": Cell(column_index_from_string("E"), "E"),
    "kg": Cell(column_index_from_string("F"), "F"),
    "remainings": Cell(column_index_from_string("G"), "G"),
    "total_output": Cell(column_index_from_string("H"), "H"),
    "delimiter": Cell(column_index_from_string("J"), "J"),
    "delimiter_int": Cell(column_index_from_string("M"), "M"),
}

ROWS = {
    "total_volume": 2,
}

SKU_SHEET_NAME: str = "SKU Маскарпоне"
PLAN_SHEET_NAME: str = "План варок"


def draw_skus(wb: openpyxl.Workbook, skus: list[SKU], sheet_name: str, row_number: int | None = None) -> int:
    excel_client = ExcelBlock(wb[sheet_name])
    if row_number is None:
        excel_client.draw_row(1, ["-", "-", "-"], set_border=False)
        row_number = 2

    for group_sku in sorted(skus, key=lambda x: x.name, reverse=False):
        boiling = group_sku.made_from_boilings[0]
        excel_client.draw_row(
            row_number,
            [group_sku.name, boiling.to_str(), boiling.output_coeff, int(boiling.output_coeff * boiling.output_kg)],
            set_border=False,
        )
        row_number += 1

    return row_number


def get_sku_color(sku_name: str, skus: list[SKU]) -> str:
    sku = next((x for x in skus if x.name == sku_name), None)
    return flask.current_app.config["COLORS"]["Default"] if sku is None else sku.colour


def draw_boiling_sheet(
    wb: openpyxl.Workbook, df: pd.DataFrame, skus: list[SKU], sheet_name: str, row_number: int | None = None
):
    if df.empty:
        return wb, row_number

    if row_number is None:
        row_number = 3

    excel_client = ExcelBlock(wb[sheet_name])
    values = []

    sku_names = [x.name for x in skus]

    for id, grp in df[df["name"].isin(sku_names)].groupby("id", sort=False):
        for i, row in grp.iterrows():
            columns = [x for x in row.index if x in COLUMNS.keys()]
            v = [row[column] for column in columns]
            c = [COLUMNS[column] for column in columns]
            values.append(dict(zip(c, v)))
        empty_columns = [
            COLUMNS["name"],
            COLUMNS["output"],
            COLUMNS["delimiter"],
        ]
        values.append(dict(zip(empty_columns, ["-"] * len(empty_columns))))

    for v in values:
        if v[COLUMNS["name"]] != "-":
            del v[COLUMNS["boiling_type"]]
            del v[COLUMNS["output"]]
        value = v.values()

        column = [x.col for x in v.keys()]
        formula = '=IF({1}{0}="-", "", 1 + SUM(INDIRECT(ADDRESS(2,COLUMN({2}{0})) & ":" & ADDRESS(ROW(),COLUMN({2}{0})))))'.format(
            row_number,
            COLUMNS["delimiter"].col_name,
            COLUMNS["delimiter_int"].col_name,
        )

        colour = get_sku_color(v[COLUMNS["name"]], skus)
        excel_client.colour = colour[1:]

        excel_client.draw_cell(
            row=row_number,
            col=COLUMNS["boiling_number"].col,
            value=formula,
            set_border=False,
        )
        excel_client.draw_row(row=row_number, values=value, cols=column, set_border=False)
        excel_client.color_cell(row=row_number, col=COLUMNS["boiling_type"].col)
        excel_client.color_cell(row=row_number, col=COLUMNS["output"].col)
        excel_client.color_cell(row=row_number, col=COLUMNS["kg_output"].col)

        row_number += 1
    return wb, row_number


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
            wb=wb, df=item.df, sheet_name=item.sheet_name, skus=item.skus, row_number=row_number
        )

    # for sheet in wb.sheetnames:
    #     wb[sheet].views.sheetView[0].tabSelected = False

    wb.active = 2
    return wb
