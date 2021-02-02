from openpyxl.styles import Alignment

from app.utils.features.openpyxl_wrapper import ExcelBlock

#
# Cel
COLUMNS_LENGTH = 11
# COLUMNS = {
#     'sku':
# }


def schedule_plan(wb, df, date):
    sheet_name = 'Печать заданий'
    water_task_name = 'Задание на упаковку линии воды Моцарельного цеха'
    salt_task_name = 'Задание на упаковку линии пиццы Моцарельного цеха'

    cur_row = 1
    space_row = 1

    wb.create_sheet(sheet_name)
    excel_client = ExcelBlock(wb['sheet_name'])
    excel_client.merge_cells(
        beg_col=2,
        beg_row=cur_row,
        end_col=2 + COLUMNS_LENGTH,
        end_row=cur_row,
        value=water_task_name,
        alignment=Alignment(horizontal='center', vertical='center', wrapText=True),
    )
    cur_row += 1
    excel_client.merge_cells(
        beg_col=2,
        beg_row=cur_row,
        end_col=2 + COLUMNS_LENGTH,
        end_row=cur_row,
        value=date,
        alignment=Alignment(horizontal='center', vertical='center', wrapText=True),
    )
    excel_client.draw_row()


    pass


def schedule_plan_boilings(df, date):
    pass