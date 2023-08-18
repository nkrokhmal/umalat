from openpyxl.utils.cell import column_index_from_string

from app.imports.runtime import *
from app.models import RicottaBoiling, RicottaSKU
from app.utils.features.openpyxl_wrapper import ExcelBlock


Cell = collections.namedtuple("Cell", "col, col_name")

COLUMNS = {
    "boiling_number": Cell(column_index_from_string("A"), "A"),
    "boiling_type": Cell(column_index_from_string("B"), "B"),
    "output": Cell(column_index_from_string("C"), "C"),
    "number_of_tanks": Cell(column_index_from_string("D"), "D"),
    "name": Cell(column_index_from_string("E"), "E"),
    "kg": Cell(column_index_from_string("F"), "F"),
    "remainings": Cell(column_index_from_string("G"), "G"),
    "total_output": Cell(column_index_from_string("I"), "I"),
    "boiling_count": Cell(column_index_from_string("Q"), "Q"),
    "delimiter": Cell(column_index_from_string("J"), "J"),
    "delimiter_int": Cell(column_index_from_string("M"), "M"),
    "total_volume": Cell(column_index_from_string("T"), "T"),
}

ROWS = {
    "total_volume": 2,
}


def draw_boiling_names(wb):
    excel_client = ExcelBlock(wb["Типы варок"])
    boiling_names = list(set([x.to_str() for x in db.session.query(RicottaBoiling).all()]))
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
                group_sku.made_from_boilings[0].to_str(),
                int(group_sku.output_per_tank * group_sku.made_from_boilings[0].number_of_tanks),
                group_sku.made_from_boilings[0].number_of_tanks,
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
    skus = db.session.query(RicottaSKU).all()
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
            COLUMNS["name"],
            COLUMNS["output"],
            COLUMNS["number_of_tanks"],
            COLUMNS["boiling_count"],
            COLUMNS["delimiter"],
        ]
        values.append(dict(zip(empty_columns, ["-"] * len(empty_columns))))

    cur_row = 3
    boiling_count = 1
    number_of_tanks = 0

    for v in values:
        current_boiling_count = v[COLUMNS["boiling_count"]]
        current_number_of_tanks = v[COLUMNS["number_of_tanks"]]

        print(current_boiling_count, current_number_of_tanks)

        del v[COLUMNS["boiling_count"]]
        del v[COLUMNS["output"]]
        del v[COLUMNS["number_of_tanks"]]

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
            excel_client.draw_cell(
                row=cur_row,
                col=COLUMNS["boiling_count"].col,
                value=int(number_of_tanks),
                set_border=False,
            )
        else:
            excel_client.color_cell(col=COLUMNS["boiling_type"].col, row=cur_row)
            excel_client.color_cell(col=COLUMNS["output"].col, row=cur_row)
            excel_client.color_cell(col=COLUMNS["number_of_tanks"].col, row=cur_row)

            number_of_tanks = current_number_of_tanks
            boiling_count = current_boiling_count

        cur_row += 1

    excel_client.font_size = 10
    excel_client.draw_cell(
        row=ROWS["total_volume"],
        col=COLUMNS["total_volume"].col,
        value=total_volume,
        set_border=False,
    )

    for sheet in wb.sheetnames:
        wb[sheet].views.sheetView[0].tabSelected = False
    wb.active = 2
    return wb
