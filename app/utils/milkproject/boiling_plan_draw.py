from app.imports.runtime import *

from openpyxl.utils.cell import column_index_from_string

from app.utils.features.merge_boiling_utils import CircularList
from app.utils.features.openpyxl_wrapper import ExcelBlock
from app.models import *

Cell = collections.namedtuple("Cell", "col, col_name")

COLUMNS = {
    "boiling_number": Cell(column_index_from_string("A"), "A"),
    "output": Cell(column_index_from_string("B"), "B"),
    "percent": Cell(column_index_from_string("C"), "C"),
    "group": Cell(column_index_from_string("D"), "D"),
    "name": Cell(column_index_from_string("E"), "E"),
    "kg": Cell(column_index_from_string("F"), "F"),
    "remainings": Cell(column_index_from_string("G"), "G"),
    "delimiter": Cell(column_index_from_string("I"), "I"),
    "delimiter_int": Cell(column_index_from_string("L"), "L"),
}

ROWS = {
    "total_volume": 2,
}

SKU_SHEET_NAME = "SKU Милкпроджект"
PLAN_SHEET_NAME = "План варок"


def draw_skus(wb, data_sku, sheet_name, cur_i=None):
    grouped_skus = data_sku
    grouped_skus.sort(key=lambda x: x.name, reverse=False)
    excel_client = ExcelBlock(wb[sheet_name])
    excel_client.draw_row(1, ["-", "-", "-"], set_border=False)
    if not cur_i:
        cur_i = 2

    for group_sku in grouped_skus:
        excel_client.draw_row(
            cur_i,
            [
                group_sku.name,
                group_sku.made_from_boilings[0].output_kg,
                group_sku.made_from_boilings[0].percent,
            ],
            set_border=False,
        )
        cur_i += 1

    return cur_i


def get_colour_by_name(sku_name, skus):
    sku = [x for x in skus if x.name == sku_name]
    if len(sku) > 0:
        return sku[0].colour
    else:
        return flask.current_app.config["COLORS"]["Default"]


def draw_boiling_sheet(
    wb, df, skus, sheet_name, cur_row=None, normalize=True
):
    print(df)
    if not cur_row:
        cur_row = 3

    if not df.empty:
        excel_client = ExcelBlock(wb[sheet_name])
        values = []

        sku_names = [x.name for x in skus]
        df_filter = df[df["name"].isin(sku_names)].copy()

        for id, grp in df_filter.groupby("id", sort=False):
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
            value = v.values()

            column = [x.col for x in v.keys()]
            formula = '=IF({1}{0}="-", "", 1 + SUM(INDIRECT(ADDRESS(2,COLUMN({2}{0})) & ":" & ADDRESS(ROW(),COLUMN({2}{0})))))'.format(
                cur_row,
                COLUMNS["delimiter"].col_name,
                COLUMNS["delimiter_int"].col_name,
            )

            colour = get_colour_by_name(v[COLUMNS["name"]], skus)
            excel_client.colour = colour[1:]

            excel_client.draw_cell(
                row=cur_row,
                col=COLUMNS["boiling_number"].col,
                value=formula,
                set_border=False,
            )
            excel_client.draw_row(
                row=cur_row, values=value, cols=column, set_border=False
            )
            excel_client.color_cell(row=cur_row, col=COLUMNS["output"].col)
            excel_client.color_cell(row=cur_row, col=COLUMNS["percent"].col)
            cur_row += 1
    return wb, cur_row


def draw_boiling_plan(df, wb):
    milkproject_skus = db.session.query(MilkProjectSKU).all()

    _ = draw_skus(wb, milkproject_skus, SKU_SHEET_NAME)
    wb, _ = draw_boiling_sheet(
        wb=wb,
        df=df,
        sheet_name=PLAN_SHEET_NAME,
        skus=milkproject_skus,
    )

    for sheet in wb.sheetnames:
        wb[sheet].views.sheetView[0].tabSelected = False
    wb.active = 2
    return wb
