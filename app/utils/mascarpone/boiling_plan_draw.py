from app.interactive_imports import *
from flask import current_app
from collections import namedtuple
from app.utils.features.merge_boiling_utils import CircularList
from app.utils.features.openpyxl_wrapper import ExcelBlock
from openpyxl.utils.cell import column_index_from_string


Cell = namedtuple("Cell", "col, col_name")

COLUMNS = {
    "boiling_number": Cell(column_index_from_string("A"), "A"),
    "boiling_type": Cell(column_index_from_string("B"), "B"),
    "output": Cell(column_index_from_string("C"), "C"),
    "fermentators": Cell(column_index_from_string("D"), "D"),
    "name": Cell(column_index_from_string("E"), "E"),
    "kg": Cell(column_index_from_string("F"), "F"),
    "remainings": Cell(column_index_from_string("G"), "G"),
    "total_output": Cell(column_index_from_string("I"), "I"),
    "boiling_count": Cell(column_index_from_string("Q"), "Q"),
    "delimiter": Cell(column_index_from_string("J"), "J"),
    "delimiter_int": Cell(column_index_from_string("M"), "M"),
}

ROWS = {
    "total_volume": 2,
}


def draw_skus(wb, data_sku, sheet_name):
    grouped_skus = data_sku
    grouped_skus.sort(key=lambda x: x.name, reverse=False)
    excel_client = ExcelBlock(wb[sheet_name])
    excel_client.draw_row(1, ["-", "-",], set_border=False)
    cur_i = 2

    for group_sku in grouped_skus:
        excel_client.draw_row(
            cur_i,
            [
                group_sku.name,
                group_sku.made_from_boilings[0].to_str(),
            ],
            set_border=False,
        )
        cur_i += 1


def draw_fermentators(wb):
    sheet_name = 'Заквасочники'
    excel_client = ExcelBlock(wb[sheet_name])
    cur_i = 2
    for fermentators in [
        ["1-2", "5", "1-2"],
        ["3-4", "6", "3-4"],
    ]:
        excel_client.draw_row(
            cur_i,
            fermentators,
            set_border=False,
        )
        cur_i += 1


def get_colour_by_name(sku_name, skus):
    sku = [x for x in skus if x.name == sku_name]
    if len(sku) > 0:
        return sku[0].colour
    else:
        return current_app.config["COLOURS"]["Default"]


def draw_boiling_sheet(wb, df, skus, sheet_name, type=None):
    excel_client = ExcelBlock(wb[sheet_name])

    if type:
        fermentator_circular = CircularList()
        fermentator_circular.create([5, 6])
        fermentator_iterator = iter(fermentator_circular)
        fermentator_number = next(fermentator_iterator)
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

    cur_row = 3

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
        excel_client.draw_row(row=cur_row, values=value, cols=column, set_border=False)

        if type:
            if v[COLUMNS["name"]] != "-":
                excel_client.draw_cell(
                    row=cur_row,
                    col=COLUMNS["fermentators"].col,
                    value=fermentator_number,
                    set_border=False,
                )
            else:
                fermentator_number = next(fermentator_iterator)
        cur_row += 1
    return wb


def draw_boiling_plan(mascarpone_df, cream_cheese_df, cream_df, wb):
    mascarpone_skus = db.session.query(MascarponeSKU).join(Group).filter(Group.name == "Маскарпоне").all()
    cream_cheese_skus = db.session.query(CreamCheeseSKU).all()
    cream_skus = db.session.query(MascarponeSKU).join(Group).filter(Group.name == "Сливки").all()

    print(cream_skus)

    draw_skus(wb, mascarpone_skus, "SKU Маскарпоне")
    draw_skus(wb, cream_cheese_skus, "SKU Крем чиз")
    draw_skus(wb, cream_skus, "SKU Сливки")

    draw_fermentators(wb)

    SkuGroup = namedtuple("SkuGroup", "df, sheet_name, skus, type")

    for item in [
        SkuGroup(mascarpone_df, "Маскарпоне", mascarpone_skus, None),
        SkuGroup(cream_cheese_df, "Крем чиз", cream_cheese_skus, "cream_cheese"),
        SkuGroup(cream_df, "Сливки", cream_skus, None)
    ]:

        wb = draw_boiling_sheet(wb=wb, df=item.df, sheet_name=item.sheet_name, skus=item.skus, type=item.type)

    for sheet in wb.sheetnames:
        wb[sheet].views.sheetView[0].tabSelected = False
    wb.active = 2
    return wb