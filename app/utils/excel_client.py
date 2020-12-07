import pandas as pd
import openpyxl
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter
import re
import json
from .openpyxl_wrapper import ExcelBlock


class Cell:
    def __init__(self, row, column, name):
        self.row = row
        self.column = column
        self.name = name


SHEETS = {
    0: 'файл остатки',
    1: 'планирование суточное'
}

COLOURS = {
    'Для пиццы': 'E5B7B6',
    'Моцарелла': 'DAE5F1',
    'Фиор ди Латте': 'CBC0D9',
    'Чильеджина': 'E5DFEC',
    'Качокавалло': 'F1DADA',
    'Сулугуни': 'F1DADA'
}

ORDER = ['Фиор ди Латте', 'Чильеджина', 'Моцарелла', 'Сулугуни', 'Для пиццы', 'Качокавалло']

CELLS = {
    'FormFactor': Cell(1, 1, 'Форм фактор'),
    'Brand': Cell(1, 2, 'Бренд'),
    'SKU': Cell(1, 3, 'Номенклатура'),
    'FactRemains': Cell(1, 4, 'Факт.остатки, заявка'),
    'NormativeRemains': Cell(1, 5, 'Нормативные остатки'),
    'ProductionPlan': Cell(1, 6, 'План производства'),
    'Estimation': Cell(1, 12, 'Расчет'),
    'Plan': Cell(1, 13, 'План'),
    'BoilingVolumes': Cell(1, 14, 'Объемы варок'),
    'Name1': Cell(1, 15, 'Фактические остатки на складах - Заявлено, кг:'),
    'Name2': Cell(2, 15, 'Нормативные остатки, кг')
}

COLUMNS = {
    'BoilingVolume': 10,
    'SKUS_ID': 18,
    'BOILING_ID': 19
}

BOILING_LIMITS = {
    'MIN': 6000,
    'MAX': 8000
}


def generate_title(sheet):
    sheet.column_dimensions[openpyxl.utils.get_column_letter(COLUMNS['SKUS_ID'])].hidden = True
    sheet.column_dimensions[openpyxl.utils.get_column_letter(COLUMNS['BOILING_ID'])].hidden = True
    for key, val in CELLS.items():
        sheet.cell(val.row, val.column).value = val.name
    sheet.freeze_panes = sheet['A2']

    sheet.column_dimensions[get_column_letter(CELLS['Brand'].column)].width = 3 * 5
    sheet.column_dimensions[get_column_letter(CELLS['SKU'].column)].width = 10 * 5
    sheet.column_dimensions[get_column_letter(COLUMNS['BoilingVolume'])].width = 5 * 5


def build_plan(date, df, request_list, plan_path=None):
    filename = '{}_{}.xlsx'.format('plan', date.strftime('%Y-%m-%d'))
    if plan_path is None:
        path = '{}/{}'.format('app/data/plan', filename)
    else:
        path = plan_path

    form_factors = set([x["GroupSKU"][0]["SKU"].form_factor for x in request_list])

    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer, sheet_name=SHEETS[0])
        writer.save()

    wb = openpyxl.load_workbook(filename=path)
    sheet_plan = wb.create_sheet(SHEETS[1])
    generate_title(sheet=sheet_plan)

    cur_row, space_rows = 2, 3
    for form_factor in ORDER:
        group_skus = [x for x in request_list if x["GroupSKU"][0]["SKU"].form_factor == form_factor]
        result_row = cur_row
        total_weight_row = (result_row + len(group_skus) + 1)
        group_sku_length = sum([len(x["GroupSKU"]) for x in group_skus])
        colour = COLOURS[group_skus[0]["GroupSKU"][0]["SKU"].form_factor]

        excel_block = ExcelBlock(sheet=sheet_plan, colour=colour)
        # создаем объем варки
        excel_block.merge_cells(
            beg_row=total_weight_row,
            end_row=total_weight_row,
            beg_col=COLUMNS['BoilingVolume'],
            end_col=COLUMNS['BoilingVolume'] + 1,
            value='Объем варки'
        )
        # Записываем данные в расчет
        excel_block.cell_value(
            row=total_weight_row,
            col=CELLS['Estimation'].column,
            value=group_skus[0]["GroupSKU"][0]["SKU"].output_per_ton
        )
        # Объединяем ячейки для записи в форм фактор
        excel_block.merge_cells(
            beg_row=cur_row,
            beg_col=CELLS['FormFactor'].column,
            end_row=cur_row + group_sku_length - 1,
            end_col=CELLS['FormFactor'].column,
            value=group_skus[0]["GroupSKU"][0]["SKU"].form_factor,
            alignment=Alignment(horizontal='center', vertical='center')
        )

        for group_sku in group_skus:
            group_formula = []
            for sku in group_sku["GroupSKU"]:
                formula_plan = "=INDEX('{0}'!$A$5:$DK$265,MATCH($O$1,'{0}'!$A$5:$A$228,0),MATCH({1},'{0}'!$A$5:$DK$5,0))".format(
                    SHEETS[0], excel_block.sheet.cell(cur_row, CELLS['SKU'].column).coordinate)
                formula_remains = "=INDEX('{0}'!$A$5:$DK$265,MATCH($O$2,'{0}'!$A$5:$A$228,0),MATCH({1},'{0}'!$A$5:$DK$5,0))".format(
                    SHEETS[0], excel_block.sheet.cell(cur_row, CELLS['SKU'].column).coordinate)

                excel_block.cell_value(row=cur_row, col=CELLS['Brand'].column, value=sku["SKU"].brand_name)
                excel_block.cell_value(row=cur_row, col=CELLS['SKU'].column, value=sku["SKU"].name)
                excel_block.cell_value(row=cur_row, col=CELLS['FactRemains'].column, value=formula_plan)
                excel_block.cell_value(row=cur_row, col=CELLS['NormativeRemains'].column, value=formula_remains)
                excel_block.cell_value(row=cur_row, col=CELLS['ProductionPlan'].column,
                                       value='=MIN({}, 0)'.format(excel_block.sheet.cell(cur_row, CELLS['FactRemains'].column).coordinate))

                group_formula.append(excel_block.sheet.cell(cur_row, CELLS['ProductionPlan'].column).coordinate)
                cur_row += 1

            excel_block.merge_cells(
                beg_row=result_row,
                beg_col=COLUMNS['BoilingVolume'],
                end_row=result_row,
                end_col=COLUMNS['BoilingVolume'] + 1,
                value='{}% варка, {}, Лактоза {}, Id {}'.format(
                    group_sku["GroupSKU"][0]["SKU"].boiling.percent,
                    group_sku["GroupSKU"][0]["SKU"].boiling.ferment,
                    group_sku["GroupSKU"][0]["SKU"].boiling.is_lactose,
                    group_sku["GroupSKU"][0]["SKU"].boiling_id
                )
            )
            formula_boiling_count = '{}'.format(str(group_formula).strip('[]').replace(',', ' +').replace('\'', "").upper())
            excel_block.cell_value(
                row=result_row,
                col=CELLS['Estimation'].column,
                value='=-({}) / {}'.format(
                    formula_boiling_count,
                    excel_block.sheet.cell(total_weight_row, CELLS['Estimation'].column).coordinate.upper())
            )
            excel_block.cell_value(
                row=result_row,
                col=CELLS['Plan'].column,
                value='=ROUND({}, 0)'.format(excel_block.sheet.cell(result_row, CELLS['Estimation'].column).coordinate)
            )
            excel_block.cell_value(
                row=result_row,
                col=COLUMNS['SKUS_ID'],
                value=str([x["SKU"].id for x in group_sku["GroupSKU"]])
            )
            excel_block.cell_value(
                row=result_row,
                col=COLUMNS['SKUS_ID'],
                value=str([x["SKU"].id for x in group_sku["GroupSKU"]])
            )
            excel_block.cell_value(
                row=result_row,
                col=COLUMNS['BOILING_ID'],
                value=group_sku["GroupSKU"][0]["SKU"].boiling_id
            )
            result_row += 1

        cur_row = max(result_row, cur_row) + space_rows

    wb.save(path)
    return '{}/{}'.format('data/plan', filename)


def parse_plan_cell(date, wb, excel, skus):
    sheet_plan = wb[SHEETS[1]]
    response = {'Date': date, 'WeekDay': date.weekday(), 'Boilings': []}
    for i in range(1, 100):
        if sheet_plan.cell(i, COLUMNS['BoilingVolume']).value is not None and \
                "Лактоза" in sheet_plan.cell(i, COLUMNS['BoilingVolume']).value:
            boilings_count = excel.evaluate("'{}'!{}".format(
                SHEETS[1],
                sheet_plan.cell(i, CELLS['Plan'].column).coordinate)
            )
            sku_ids = sheet_plan.cell(i, COLUMNS['SKUS_ID']).value
            boiling_id = sheet_plan.cell(i, COLUMNS['BOILING_ID']).value
            sku_group = [sku for sku in skus if sku.id in json.loads(sku_ids)]

            sku_volumes = {}
            for j in range(1, 100):
                if sheet_plan.cell(j, CELLS['SKU'].column).value in [x.name for x in sku_group]:
                    sku_id = [x.id for x in sku_group if x.name == sheet_plan.cell(j, CELLS['SKU'].column).value][0]
                    volume = abs(excel.evaluate("'{}'!{}".format(
                        SHEETS[1],
                        sheet_plan.cell(j, CELLS['ProductionPlan'].column).coordinate)
                    ))
                    sku_volumes[sku_id] = volume

            boiling_weights = []
            if sheet_plan.cell(i, CELLS['BoilingVolumes'].column).value is not None:
                boiling_weights = re.split(', |. | ', sheet_plan.cell(i, CELLS['BoilingVolumes'].column).value)
                boiling_weights = [x for x in boiling_weights if BOILING_LIMITS['MIN'] <= int(x) <= BOILING_LIMITS['MAX']]
                boiling_weights = [int(x) for x in boiling_weights if isinstance(x, int) or x.isdigit()]

            if len(boiling_weights) > boilings_count:
                boiling_weights = boilings_count * [BOILING_LIMITS['MAX']]
            else:
                boiling_weights += int(boilings_count - len(boiling_weights)) * [BOILING_LIMITS['MAX']]
            response['Boilings'].append({
                "BoilingId": boiling_id,
                "BoilingCount": boilings_count,
                "BoilingWeights": boiling_weights,
                "SKUVolumes": sku_volumes
            })

    response['Boilings'] = [x for x in response['Boilings'] if x['BoilingCount'] > 0]
    return response
