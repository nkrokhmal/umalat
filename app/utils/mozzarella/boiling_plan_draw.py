from collections import namedtuple

from openpyxl.utils.cell import column_index_from_string

from app.imports.runtime import *
from app.models import FormFactor, MozzarellaBoiling, MozzarellaLine, MozzarellaSKU
from app.utils.features.db_utils import sku_is_rubber
from app.utils.features.openpyxl_wrapper import ExcelBlock


Cell = namedtuple("Cell", "col, col_name")

COLUMNS = {
    "boiling_number": Cell(column_index_from_string("A"), "A"),
    "boiling_name": Cell(column_index_from_string("B"), "B"),
    "boiling_volume": Cell(column_index_from_string("C"), "C"),
    "group": Cell(column_index_from_string("D"), "D"),
    "form_factor": Cell(column_index_from_string("E"), "E"),
    "boiling_form_factor": Cell(column_index_from_string("F"), "F"),
    "packer": Cell(column_index_from_string("G"), "G"),
    "name": Cell(column_index_from_string("H"), "H"),
    "kg": Cell(column_index_from_string("I"), "I"),
    # "orig_kg": Cell(column_index_from_string("I"), "I"),
    "remainings": Cell(column_index_from_string("J"), "J"),
    "team_number": Cell(column_index_from_string("K"), "K"),
    "cleaning": Cell(column_index_from_string("L"), "L"),
    "boiling_configuration": Cell(column_index_from_string("M"), "M"),
    "total_boiling_volume": Cell(column_index_from_string("N"), "N"),
    "delimiter": Cell(column_index_from_string("O"), "O"),
    "delimiter_int": Cell(column_index_from_string("R"), "R"),
}


def draw_boiling_names(wb):
    excel_client = ExcelBlock(wb["Типы варок"])
    boiling_names = list(set([x.to_str() for x in db.session.query(MozzarellaBoiling).all()]))
    excel_client.draw_row(1, ["-"])
    cur_i = 2
    for boiling_name in boiling_names:
        excel_client.draw_row(cur_i, [boiling_name], set_border=False)
        cur_i += 1


def draw_extra_packing(wb, df, skus):
    excel_client = ExcelBlock(wb["Дополнительная фасовка"])
    cur_i = 2
    for value in df.values:
        if value[0] in [sku.name for sku in skus if not sku.packing_by_request]:
            excel_client.draw_row(cur_i, value, set_border=False)
            cur_i += 1


def draw_form_factors(wb, form_factors):
    excel_client = ExcelBlock(wb["Форм фактор плавления"])
    cur_i = 1
    for value in sorted(form_factors, key=lambda x: x.weight_with_line):
        excel_client.draw_row(cur_i, [value.weight_with_line], set_border=False)
        cur_i += 1


def draw_skus_sheet(wb, type_sku, data_sku):
    grouped_skus = data_sku[type_sku]
    grouped_skus.sort(key=lambda x: x.name, reverse=False)
    excel_client = ExcelBlock(wb["{} SKU".format(type_sku)])
    excel_client.draw_row(1, ["-", "-", "-"], set_border=False)
    cur_i = 2

    for group_sku in grouped_skus:
        team_number = "2" if "Терка" in group_sku.form_factor.name else "1"

        excel_client.draw_row(
            cur_i,
            [group_sku.name, group_sku.made_from_boilings[0].to_str(), team_number],
            set_border=False,
        )
        cur_i += 1


def draw_skus(wb, skus):
    skus.sort(key=lambda x: x.name, reverse=False)
    excel_client = ExcelBlock(wb["Вода SKU"])
    excel_client.draw_row(1, ["-", "-"], set_border=False)
    cur_i = 2

    for group_sku in skus:
        excel_client.draw_row(
            cur_i,
            [group_sku.name, group_sku.made_from_boilings[0].to_str()],
            set_border=False,
        )
        cur_i += 1


def get_colour_by_name(sku_name, skus):
    sku = [x for x in skus if x.name == sku_name]
    if len(sku) > 0:
        return sku[0].colour
    else:
        return flask.current_app.config["COLORS"]["Default"]


def draw_boiling_plan(df, df_extra, wb):
    skus = db.session.query(MozzarellaSKU).all()
    line_kg = db.session.query(MozzarellaLine).all()[0].input_ton
    form_factors = db.session.query(FormFactor).all()
    data_sku = {
        "Вода": [x for x in skus if x.made_from_boilings[0].boiling_type == "water"],
        "Соль": [x for x in skus if x.made_from_boilings[0].boiling_type == "salt"],
    }
    draw_boiling_names(wb=wb)
    draw_extra_packing(wb=wb, df=df_extra, skus=skus)
    draw_form_factors(wb=wb, form_factors=form_factors)
    for sheet_name in ["Соль", "Вода"]:
        draw_skus_sheet(wb, sheet_name, data_sku)

        values = []
        excel_client = ExcelBlock(wb[sheet_name])

        sku_names = [x.name for x in data_sku[sheet_name]]
        df_filter = df[df["name"].isin(sku_names)].copy()
        for id, grp in df_filter.groupby("id", sort=False):
            for i, row in grp.iterrows():
                columns = [x for x in row.index if x in COLUMNS.keys()]
                v = [row[column] for column in columns]
                c = [COLUMNS[column] for column in columns]
                values.append(dict(zip(c, v)))
            empty_columns = [
                COLUMNS["boiling_name"],
                COLUMNS["boiling_volume"],
                COLUMNS["group"],
                COLUMNS["form_factor"],
                COLUMNS["boiling_form_factor"],
                COLUMNS["packer"],
                COLUMNS["name"],
                COLUMNS["delimiter"],
            ]
            values.append(dict(zip(empty_columns, ["-"] * len(empty_columns))))
        cur_row = 2
        for v in values:
            value = v.values()
            column = [x.col for x in v.keys()]
            if sheet_name == "Вода":
                formula = '=IF({1}{0}="-", "", 1 + SUM(INDIRECT(ADDRESS(2,COLUMN({2}{0})) & ":" & ADDRESS(ROW(),COLUMN({2}{0})))))'.format(
                    cur_row,
                    COLUMNS["delimiter"].col_name,
                    COLUMNS["delimiter_int"].col_name,
                )
            else:
                formula = '=IF({1}{0}="-", "-", 1 + MAX(\'Вода\'!$A$2:$A$100) + SUM(INDIRECT(ADDRESS(2,COLUMN({2}{0})) & ":" & ADDRESS(ROW(),COLUMN({2}{0})))))'.format(
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
            if sku_is_rubber(skus, v[COLUMNS["name"]]):
                pass
                # excel_client.draw_cell(
                #     row=cur_row,
                #     col=COLUMNS["team_number"].col,
                #     value=2,
                #     set_border=False,
                #     set_colour=False,
                # )
            elif v[COLUMNS["name"]] == "-":
                excel_client.draw_cell(
                    row=cur_row,
                    col=COLUMNS["team_number"].col,
                    value="",
                    set_border=False,
                )
                excel_client.draw_cell(
                    row=cur_row,
                    col=COLUMNS["boiling_configuration"].col,
                    value=line_kg,
                    set_border=False,
                )
            else:
                pass
                # excel_client.draw_cell(
                #     row=cur_row,
                #     col=COLUMNS["team_number"].col,
                #     value=1,
                #     set_border=False,
                #     set_colour=False,
                # )
            cur_row += 1
    for sheet in wb.sheetnames:
        wb[sheet].views.sheetView[0].tabSelected = False
    wb.active = 2
    return wb


def draw_boiling_plan_merged(df, wb):
    line_kg = db.session.query(MozzarellaLine).all()[0].input_ton
    skus = db.session.query(MozzarellaSKU).all()
    sheet_name = "План варок"

    values = []
    excel_client = ExcelBlock(wb[sheet_name])

    draw_boiling_names(wb=wb)
    draw_skus(wb, skus)

    for id, grp in df.groupby("id", sort=False):
        for i, row in grp.iterrows():
            columns = [x for x in row.index if x in COLUMNS.keys()]
            v = [row[column] for column in columns]
            c = [COLUMNS[column] for column in columns]
            values.append(dict(zip(c, v)))
        empty_columns = [
            COLUMNS["boiling_name"],
            COLUMNS["boiling_volume"],
            COLUMNS["group"],
            COLUMNS["form_factor"],
            COLUMNS["boiling_form_factor"],
            COLUMNS["packer"],
            COLUMNS["name"],
            COLUMNS["delimiter"],
            COLUMNS["boiling_configuration"],
        ]
        values.append(dict(zip(empty_columns, ["-"] * len(empty_columns))))

    cur_row = 2

    configuration = 0
    for v in values:
        cur_configuration = v[COLUMNS["boiling_configuration"]]
        del v[COLUMNS["boiling_configuration"]]

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
                col=COLUMNS["boiling_configuration"].col,
                value=configuration,
                set_border=False,
            )
        else:
            configuration = int(line_kg * cur_configuration / v[COLUMNS["boiling_volume"]])
        cur_row += 1

    return wb
