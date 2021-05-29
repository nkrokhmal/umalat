import flask
import pandas as pd

from app.imports.runtime import *

from openpyxl.styles import Alignment
from openpyxl.utils.cell import coordinate_from_string, column_index_from_string

from app.enum import LineName
from app.utils.features.openpyxl_wrapper import ExcelBlock
from app.utils.features.draw_utils import *
from collections import namedtuple


def update_total_schedule_task(date, df, df_packing=None):
    folder = flask.current_app.config["TOTAL_SCHEDULE_TASK_FOLDER"]
    path = os.path.join(folder, f"{date.date()}.csv")
    columns = ['sku', 'code', 'in_box', 'kg', 'boxes_count']
    if not os.path.exists(path):
        df_task = pd.DataFrame(columns=columns)
        df_task.to_csv(path, index=False)

    df_task = pd.read_csv(path)
    skus = df_task.sku
    for sku_name, grp in df.groupby("sku_name"):
        if grp.iloc[0]["sku"].group.name != "Качокавалло":
            kg = round(grp["original_kg"].sum())
            boxes_count = math.ceil(
                1000
                * grp["original_kg"].sum()
                / grp.iloc[0]["sku"].in_box
                / grp.iloc[0]["sku"].weight_netto
            )
            values = [sku_name, grp.iloc[0]["sku"].code, grp.iloc[0]["sku"].in_box, kg, boxes_count]
            if sku_name in skus:
                df_task.loc[df_task.sku == values[0], columns] = values
            else:
                df_task = df_task.append(dict(zip(columns, values)), ignore_index=True)

    if df_packing is not None:
        for i, row in df_packing.iterrows():
            boxes_count = math.ceil(
                1000
                * row["kg"]
                / row["sku_obj"].in_box
                / row["sku_obj"].weight_netto
            )
            values = [row["sku"], row["sku_obj"].code, row["sku_obj"].in_box, row["kg"], boxes_count]
            if sku_name in skus:
                df_task.loc[df_task.sku == values[0], columns] = values
            else:
                df_task = df_task.append(dict(zip(columns, values)), ignore_index=True)

    df_task.to_csv(path, index=False)


def draw_task_original(excel_client, df, date, cur_row, line_name, task_name, df_packing=None):
    df_filter = df[df["line"] == line_name]
    index = 1

    cur_row, excel_client = draw_header(excel_client, date, cur_row, task_name)

    for sku_name, grp in df_filter.groupby("sku_name"):
        if grp.iloc[0]["sku"].group.name != "Качокавалло":
            kg = round(grp["original_kg"].sum())
            boxes_count = math.ceil(
                1000
                * grp["original_kg"].sum()
                / grp.iloc[0]["sku"].in_box
                / grp.iloc[0]["sku"].weight_netto
            )
        else:
            kg = ""
            boxes_count = ""
        values = [index, sku_name, grp.iloc[0]["sku"].in_box, kg, boxes_count, grp.iloc[0]["sku"].code]
        excel_client, cur_row = draw_schedule_raw(excel_client, cur_row, values)
        index += 1

    if df_packing is not None:
        for i, row in df_packing.iterrows():
            boxes_count = math.ceil(
                1000
                * row["kg"]
                / row["sku_obj"].in_box
                / row["sku_obj"].weight_netto
            )
            values = [index, row["sku"], row["sku_obj"].in_box, row["kg"], boxes_count, row["sku_obj"].code]
            excel_client, cur_row = draw_schedule_raw(excel_client, cur_row, values, COLOR_PACKING)
            index += 1
            index += 1

    return cur_row


def draw_task_new(excel_client, df, date, cur_row, line_name, task_name, batch_number, df_packing=None):
    df_filter = df[df["line"] == line_name]

    cur_row, excel_client = draw_header(excel_client, date, cur_row, task_name, "варки")
    for boiling_group_id, grp in df_filter.groupby("group_id"):
        for i, row in grp.iterrows():
            if row["sku"].group.name != "Качокавалло":
                kg = round(row["original_kg"])
                boxes_count = math.ceil(
                    1000 * row["original_kg"] / row["sku"].in_box / row["sku"].weight_netto
                )
            else:
                kg = ""
                boxes_count = ""

            values = [boiling_group_id + batch_number - 1, row["sku_name"], row["sku"].in_box, kg, boxes_count, row["sku"].code]
            excel_client, cur_row = draw_schedule_raw(excel_client, cur_row, values)
        excel_client = draw_blue_line(excel_client, cur_row)
        cur_row += 1

    if df_packing is not None:
        for i, row in df_packing.iterrows():
            kg = round(row["kg"])
            boxes_count = math.ceil(
                1000 * row["kg"] / row["sku_obj"].in_box / row["sku_obj"].weight_netto
            )
            values = ["", row["sku"], row["sku_obj"].in_box, kg, boxes_count, row["sku_obj"].code]
            excel_client, cur_row = draw_schedule_raw(excel_client, cur_row, values, COLOR_PACKING)

        excel_client = draw_blue_line(excel_client, cur_row)
        cur_row += 1

    return cur_row


def schedule_task(wb, df, df_packing, date):
    df_copy = df.copy()
    sheet_name = "Печать заданий"
    water_task_name = "Задание на упаковку линии воды Моцарельного цеха"
    salt_task_name = "Задание на упаковку линии пиццы Моцарельного цеха"
    df_copy["line"] = df_copy["line"].apply(lambda x: x.name)

    cur_row = 2
    space_row = 4

    wb.create_sheet(sheet_name)
    excel_client = ExcelBlock(wb[sheet_name], font_size=9)

    cur_row = draw_task_original(
        excel_client, df_copy, date, cur_row, LineName.WATER, water_task_name
    )
    cur_row += space_row

    draw_task_original(
        excel_client, df_copy, date, cur_row, LineName.SALT, salt_task_name, df_packing,
    )
    return wb


def schedule_task_boilings(wb, df, df_packing, date, batch_number):
    df_copy = df.copy()
    sheet_name = "Печать заданий 2"
    water_task_name = "Задание на упаковку линии воды Моцарельного цеха"
    salt_task_name = "Задание на упаковку линии пиццы Моцарельного цеха"
    df_copy["line"] = df_copy["line"].apply(lambda x: x.name)

    cur_row = 2
    space_row = 4

    wb.create_sheet(sheet_name)
    excel_client = ExcelBlock(wb[sheet_name], font_size=9)

    cur_row = draw_task_new(
        excel_client,
        df_copy,
        date,
        cur_row,
        LineName.WATER,
        water_task_name,
        batch_number,
    )
    cur_row += space_row

    draw_task_new(
        excel_client,
        df_copy,
        date,
        cur_row,
        LineName.SALT,
        salt_task_name,
        batch_number,
        df_packing,
    )
    return wb