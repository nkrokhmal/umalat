import openpyxl
import pandas as pd

from openpyxl.utils.cell import column_index_from_string

from app.imports.runtime import *
from app.models import RicottaBoiling, RicottaSKU
from app.utils.features.openpyxl_wrapper import ExcelBlock


Cell = collections.namedtuple("Cell", "col, col_name")

COLUMNS = {
    "boiling_number": Cell(column_index_from_string("A"), "A"),
    "boiling_type": Cell(column_index_from_string("B"), "B"),
    "output_kg": Cell(column_index_from_string("C"), "C"),
    "name": Cell(column_index_from_string("D"), "D"),
    "kg": Cell(column_index_from_string("E"), "E"),
    "remainings": Cell(column_index_from_string("F"), "F"),
    "total_output": Cell(column_index_from_string("G"), "G"),
    "boiling_count": Cell(column_index_from_string("P"), "P"),
    "delimiter": Cell(column_index_from_string("I"), "I"),
    "delimiter_int": Cell(column_index_from_string("L"), "L"),
    "total_volume": Cell(column_index_from_string("Q"), "Q"),
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


def draw_skus(wb: openpyxl.Workbook, skus):
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


def get_colour_by_name(sku_name: str, skus: list[RicottaSKU]) -> str:
    sku = next((x for x in skus if x.name == sku_name), None)
    if sku is not None:
        return sku[0]
    else:
        return flask.current_app.config["COLORS"]["Default"]


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
