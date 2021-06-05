from app.imports.runtime import *
from app.utils.features.openpyxl_wrapper import ExcelBlock


def draw_additional_packing(wb, packing_df):
    sheet_name = "Дополнительная фасовка"

    if sheet_name not in wb.sheetnames:
        wb.create_sheet(sheet_name)

    excel_client = ExcelBlock(wb[sheet_name])
    cur_row = 2
    packing_df["kg_min"] = - packing_df["kg"]

    for _, row in packing_df[['sku', 'kg_min']].iterrows():
        excel_client.draw_row(cur_row, row.values)
        cur_row += 1

    return wb