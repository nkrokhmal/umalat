import os
from flask import current_app
from openpyxl.styles import Alignment
from collections import namedtuple
import math
from app.enum import LineName
from app.utils.features.openpyxl_wrapper import ExcelBlock
from openpyxl.utils.cell import coordinate_from_string, column_index_from_string


Cell = namedtuple('Cell', 'col, col_name')
COLOR = '#dce6f2'
COLUMNS = {
    'index': Cell(column_index_from_string('B'), 'B'),
    'sku': Cell(column_index_from_string('C'), 'C'),
    'boxes': Cell(column_index_from_string('I'), 'I'),
    'kg': Cell(column_index_from_string('J'), 'J'),
    'boxes_count': Cell(column_index_from_string('K'), 'K'),
    'priority': Cell(column_index_from_string('L'), 'L'),
}


def draw_header(excel_client, date, cur_row, task_name, is_boiling=None):
    alignment = Alignment(horizontal='center', vertical='center', wrapText=True)
    excel_client.raw_dimension(cur_row, 24)
    excel_client.merge_cells(
        beg_col=COLUMNS['index'].col,
        beg_row=cur_row,
        end_col=COLUMNS['priority'].col,
        end_row=cur_row,
        value=task_name,
        alignment=alignment,
        is_bold=True,
        font_size=10,
    )
    cur_row += 1

    excel_client.raw_dimension(cur_row, 24)
    excel_client.merge_cells(
        beg_col=COLUMNS['index'].col,
        beg_row=cur_row,
        end_col=COLUMNS['priority'].col,
        end_row=cur_row,
        value=date.date(),
        alignment=alignment,
        is_bold=True,
        font_size=10,
    )
    cur_row += 1

    excel_client.raw_dimension(cur_row, 24)
    excel_client.colour = COLOR[1:]
    excel_client.draw_cell(col=COLUMNS['index'].col, row=cur_row,
                           value='Номер {}'.format(is_boiling) if is_boiling is not None else 'Номер',
                           alignment=alignment)
    excel_client.merge_cells(
        beg_col=COLUMNS['sku'].col,
        beg_row=cur_row,
        end_col=COLUMNS['boxes'].col - 1,
        end_row=cur_row,
        value='Номенклатура',
        alignment=alignment,
    )
    excel_client.draw_cell(col=COLUMNS['boxes'].col, row=cur_row, value='Вложение коробок', alignment=alignment)
    excel_client.draw_cell(col=COLUMNS['kg'].col, row=cur_row, value='Вес, кг', alignment=alignment)
    excel_client.draw_cell(col=COLUMNS['boxes_count'].col, row=cur_row, value='Кол-во коробок, шт', alignment=alignment)
    excel_client.draw_cell(col=COLUMNS['priority'].col, row=cur_row, value='В первую очередь', alignment=alignment)
    cur_row += 1
    return cur_row, excel_client


def draw_task_original(excel_client, df, date, cur_row, line_name, task_name):
    df_filter = df[df['line'] == line_name]
    index = 1

    cur_row, excel_client = draw_header(excel_client, date, cur_row, task_name)

    for sku_name, grp in df_filter.groupby('sku_name'):
        excel_client.colour = COLOR[1:]
        excel_client.draw_cell(col=COLUMNS['index'].col, row=cur_row, value=index)
        excel_client.colour = None
        excel_client.merge_cells(
            beg_col=COLUMNS['sku'].col,
            beg_row=cur_row,
            end_col=COLUMNS['boxes'].col - 1,
            end_row=cur_row,
            value=sku_name
        )
        excel_client.draw_cell(col=COLUMNS['boxes'].col, row=cur_row, value=grp.iloc[0]['sku'].boxes)
        excel_client.draw_cell(col=COLUMNS['kg'].col, row=cur_row, value=grp['kg'].sum())
        excel_client.draw_cell(col=COLUMNS['boxes_count'].col, row=cur_row, value=math.ceil(1000 * grp['kg'].sum()/grp.iloc[0]['sku'].boxes/grp.iloc[0]['sku'].weight_netto))
        excel_client.draw_cell(col=COLUMNS['priority'].col, row=cur_row, value='')
        cur_row += 1
        index += 1
    return cur_row


def draw_task_new(excel_client, df, date, cur_row, line_name, task_name, batch_number):
    df_filter = df[df['line'] == line_name]

    cur_row, excel_client = draw_header(excel_client, date, cur_row, task_name, 'варки')
    for boiling_group_id, grp in df_filter.groupby('group_id'):
        for i, row in grp.iterrows():
            excel_client.colour = COLOR[1:]
            excel_client.draw_cell(col=COLUMNS['index'].col, row=cur_row, value=boiling_group_id + batch_number - 1)
            excel_client.colour = None
            excel_client.merge_cells(
                beg_col=COLUMNS['sku'].col,
                beg_row=cur_row,
                end_col=COLUMNS['boxes'].col - 1,
                end_row=cur_row,
                value=row['sku_name']
            )
            excel_client.draw_cell(col=COLUMNS['boxes'].col, row=cur_row, value=row['sku'].boxes)
            excel_client.draw_cell(col=COLUMNS['kg'].col, row=cur_row, value=row['kg'])
            excel_client.draw_cell(
                col=COLUMNS['boxes_count'].col,
                row=cur_row,
                value=math.ceil(1000 * row['kg']/row['sku'].boxes/row['sku'].weight_netto))
            excel_client.draw_cell(col=COLUMNS['priority'].col, row=cur_row, value='')
            cur_row += 1

        excel_client.draw_cell(col=COLUMNS['index'].col, row=cur_row, value='')
        excel_client.merge_cells(
            beg_col=COLUMNS['sku'].col,
            beg_row=cur_row,
            end_col=COLUMNS['boxes'].col - 1,
            end_row=cur_row,
            value='',
        )
        excel_client.draw_cell(col=COLUMNS['boxes'].col, row=cur_row, value='')
        excel_client.draw_cell(col=COLUMNS['kg'].col, row=cur_row, value='')
        excel_client.draw_cell(col=COLUMNS['boxes_count'].col, row=cur_row, value='')
        excel_client.draw_cell(col=COLUMNS['priority'].col, row=cur_row, value='')
        cur_row += 1
    return cur_row


def schedule_task(wb, df, date):
    df_copy = df.copy()
    sheet_name = 'Печать заданий'
    water_task_name = 'Задание на упаковку линии воды Моцарельного цеха'
    salt_task_name = 'Задание на упаковку линии пиццы Моцарельного цеха'
    df_copy['line'] = df_copy['line'].apply(lambda x: x.name)

    cur_row = 2
    space_row = 4

    wb.create_sheet(sheet_name)
    excel_client = ExcelBlock(wb[sheet_name])

    cur_row = draw_task_original(excel_client, df_copy, date, cur_row, LineName.WATER, water_task_name)
    cur_row += space_row

    draw_task_original(excel_client, df_copy, date, cur_row, LineName.SALT, salt_task_name)
    return wb


def schedule_task_boilings(wb, df, date, batch_number):
    df_copy = df.copy()
    sheet_name = 'Печать заданий 2'
    water_task_name = 'Задание на упаковку линии воды Моцарельного цеха'
    salt_task_name = 'Задание на упаковку линии пиццы Моцарельного цеха'
    df_copy['line'] = df_copy['line'].apply(lambda x: x.name)

    cur_row = 2
    space_row = 4

    wb.create_sheet(sheet_name)
    excel_client = ExcelBlock(wb[sheet_name])

    cur_row = draw_task_new(excel_client, df_copy, date, cur_row, LineName.WATER, water_task_name, batch_number)
    cur_row += space_row

    draw_task_new(excel_client, df_copy, date, cur_row, LineName.SALT, salt_task_name, batch_number)
    return wb