from app.utils.features.draw_utils import *
from app.utils.features.openpyxl_wrapper import ExcelBlock


def update_total_schedule_task(date, df):
    folder = flask.current_app.config["TOTAL_SCHEDULE_TASK_FOLDER"]
    path = os.path.join(folder, f"{date.date()}.csv")
    columns = ['sku', 'code', 'in_box', 'kg', 'boxes_count']
    if not os.path.exists(path):
        df_task = pd.DataFrame(columns=columns)
        df_task.to_csv(path, index=False)

    df_task = pd.read_csv(path)
    skus = df_task.sku
    for sku_name, grp in df.groupby("sku_name"):
        kg = round(grp["kg"].sum())
        boxes_count = math.ceil(
            grp["kg"].sum()
            / grp.iloc[0]["sku"].in_box
            / grp.iloc[0]["sku"].weight_netto
        )
        values = [sku_name, grp.iloc[0]["sku"].code, grp.iloc[0]["sku"].in_box, kg, boxes_count]
        if sku_name in skus:
            df_task.loc[df_task.sku == values[0], columns] = values
        else:
            df_task = df_task.append(dict(zip(columns, values)), ignore_index=True)
    df_task.to_csv(path, index=False)


def draw_task_original(excel_client, df, date, cur_row, task_name):
    df_filter = df
    index = 1

    cur_row, excel_client = draw_header(excel_client, date, cur_row, task_name)

    for sku_name, grp in df_filter.groupby("sku_name"):
        kg = round(grp["kg"].sum())
        boxes_count = math.ceil(
            grp["kg"].sum()
            / grp.iloc[0]["sku"].in_box
            / grp.iloc[0]["sku"].weight_netto
        )
        values = [index, sku_name, grp.iloc[0]["sku"].in_box, kg, boxes_count, grp.iloc[0]["sku"].code]
        excel_client, cur_row = draw_schedule_raw(excel_client, cur_row, values)
        index += 1
    return cur_row


def schedule_task_boilings(wb, df, date, batch_number):
    df_copy = df.copy()
    df_copy["sku_name"] = df_copy["sku"].apply(lambda sku: sku.name)
    sheet_name = "Печать заданий"
    ricotta_task_name = "Задание на упаковку Рикоттного цеха"

    cur_row = 2
    space_row = 4

    wb.create_sheet(sheet_name)
    excel_client = ExcelBlock(wb[sheet_name], font_size=9)

    cur_row = draw_task_original(
        excel_client,
        df_copy,
        date,
        cur_row,
        ricotta_task_name,
    )
    cur_row += space_row
    return wb
