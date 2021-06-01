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
    df["sku_name"] = df["sku"].apply(lambda x: x.name)
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
    df_task.to_csv(path, index=False, sep=';')


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
