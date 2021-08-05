from app.imports.runtime import *

from openpyxl.utils.cell import column_index_from_string

from app.utils.features.openpyxl_wrapper import ExcelBlock
from app.models import AdygeaBoiling, AdygeaSKU


Cell = collections.namedtuple("Cell", "col, col_name")

COLUMNS = {
    "boiling_number": Cell(column_index_from_string("A"), "A"),
    "group": Cell(column_index_from_string("B"), "B"),
    "output": Cell(column_index_from_string("C"), "C"),
    "name": Cell(column_index_from_string("D"), "D"),
    "kg": Cell(column_index_from_string("E"), "E"),
    "boiling_count": Cell(column_index_from_string("F"), "F"),
    "remainings": Cell(column_index_from_string("G"), "G"),
    "total_output": Cell(column_index_from_string("H"), "H"),
    "delimiter": Cell(column_index_from_string("I"), "I"),
    "delimiter_int": Cell(column_index_from_string("L"), "L"),
}

ROWS = {
    "total_volume": 2,
}


def draw_boiling_names(wb):
    excel_client = ExcelBlock(wb["Группы"])
    boiling_names = ["Кавказский", "Черкесский", "Качорикотта"]
    excel_client.draw_row(1, ["-"])
    cur_i = 2
    for boiling_name in boiling_names:
        excel_client.draw_row(cur_i, [boiling_name], set_border=False)
        cur_i += 1


def draw_skus(wb, data_sku):
    grouped_skus = data_sku
    grouped_skus.sort(key=lambda x: x.name, reverse=False)
    excel_client = ExcelBlock(wb["SKU"])
    excel_client.draw_row(1, ["-", "-", "-", "-"], set_border=False)
    cur_i = 2

    for group_sku in grouped_skus:
        excel_client.draw_row(
            cur_i,
            [
                group_sku.name,
                group_sku.group.name,
                group_sku.made_from_boilings[0].output_kg,
            ],
            set_border=False,
        )
        cur_i += 1


def get_colour_by_name(sku_name, skus):
    sku = [x for x in skus if x.name == sku_name]
    if len(sku) > 0:
        return sku[0].colour
    else:
        return flask.current_app.config["COLORS"]["Default"]


def draw_boiling_plan(df, df_extra, wb, total_volume=0):
    skus = db.session.query(AdygeaSKU).all()
    draw_boiling_names(wb=wb)
    sheet_name = "План варок"
    draw_skus(wb, skus)

    values = []
    excel_client = ExcelBlock(wb[sheet_name])

    sku_names = [x.name for x in skus]
    df_filter = df[df["name"].isin(sku_names)].copy()

    for id, grp in df_filter.groupby("id", sort=False):
        for i, row in grp.iterrows():
            columns = [x for x in row.index if x in COLUMNS.keys()]
            v = [row[column] for column in columns]
            c = [COLUMNS[column] for column in columns]
            values.append(dict(zip(c, v)))
        empty_columns = [
            COLUMNS["group"],
            COLUMNS["name"],
            COLUMNS["output"],
            COLUMNS["boiling_count"],
            COLUMNS["delimiter"],
        ]
        values.append(dict(zip(empty_columns, ["-"] * len(empty_columns))))

    cur_row = 3

    for v in values:
        del v[COLUMNS["output"]]

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
        excel_client.draw_row(row=cur_row, values=value, cols=column, set_border=False)
        if v[COLUMNS["name"]] == "-":
            pass
        else:
            excel_client.color_cell(col=COLUMNS["group"].col, row=cur_row)
            excel_client.color_cell(col=COLUMNS["output"].col, row=cur_row)
            excel_client.color_cell(col=COLUMNS["total_output"].col, row=cur_row)

        cur_row += 1

    excel_client.font_size = 10

    for sheet in wb.sheetnames:
        wb[sheet].views.sheetView[0].tabSelected = False
    wb.active = 2
    return wb
