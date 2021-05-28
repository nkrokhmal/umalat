from app.utils.features.draw_utils import *
from app.utils.features.openpyxl_wrapper import ExcelBlock


def draw_task_new(excel_client, df, date, cur_row, task_name, batch_number):
    cur_row, excel_client = draw_header(excel_client, date, cur_row, task_name, "варки")
    for boiling_group_id, grp in df.groupby("boiling_id"):
        for i, row in grp.iterrows():
            if row["sku"].in_box:
                kg = round(row["kg"])
                boxes_count = math.ceil(
                    row["kg"] / row["sku"].in_box / row["sku"].weight_netto
                )
            else:
                kg = round(row["kg"])
                boxes_count = ""

            values = [boiling_group_id + batch_number - 1, row["sku_name"], row["sku"].in_box, kg, boxes_count, row["sku"].code]
            excel_client, cur_row = draw_schedule_raw(excel_client, cur_row, values)
        excel_client = draw_blue_line(excel_client, cur_row)
        cur_row += 1
    return cur_row


def schedule_task_boilings(wb, df, date, batch_number):
    df_copy = df.copy()
    df_copy["sku_name"] = df_copy["sku"].apply(lambda sku: sku.name)
    sheet_name = "Печать заданий"
    mascarpone_task_name = "Задание на упаковку Маскарпонного цеха"

    cur_row = 2
    space_row = 4

    wb.create_sheet(sheet_name)
    excel_client = ExcelBlock(wb[sheet_name], font_size=9)

    cur_row = draw_task_new(
        excel_client,
        df_copy,
        date,
        cur_row,
        mascarpone_task_name,
        batch_number,
    )
    cur_row += space_row
    return wb
