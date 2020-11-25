import pandas as pd
import openpyxl
from openpyxl.styles import Alignment, PatternFill
import re
import json


class Cell:
    def __init__(self, row, column, coordinate):
        self.row = row
        self.column = column
        self.coordinate = coordinate


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

CELLS = {
    'Форм фактор': Cell(1, 1, 'A1'),
    'Бренд': Cell(1, 2, 'B1'),
    'Номенклатура': Cell(1, 3, 'C1'),
    'Факт.остатки, заявка': Cell(1, 4, 'D1'),
    'Нормативные остатки': Cell(1, 5, 'F1'),
    'План производства': Cell(1, 6, 'F1'),
    'Расчет': Cell(1, 12, 'K1'),
    'План': Cell(1, 13, 'M1'),
    'Объемы варок': Cell(1, 14, 'N1'),
    'Фактические остатки на складах - Заявлено, кг:': Cell(1, 15, 'O1'),
    'Нормативные остатки, кг': Cell(2, 15, 'O2')
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


def parse_plan_cell(date, wb, excel, skus):
    sheet_plan = wb[SHEETS[1]]
    response = {'Date': date, 'WeekDay': date.weekday(), 'Boilings': []}
    for i in range(1, 100):
        if sheet_plan.cell(i, COLUMNS['BoilingVolume']).value is not None and \
                "Лактоза" in sheet_plan.cell(i, COLUMNS['BoilingVolume']).value:
            boilings_count = excel.evaluate("'{}'!{}".format(
                SHEETS[1],
                sheet_plan.cell(i, CELLS['План'].column).coordinate)
            )
            sku_ids = sheet_plan.cell(i, COLUMNS['SKUS_ID']).value
            boiling_id = sheet_plan.cell(i, COLUMNS['BOILING_ID']).value
            sku_group = [sku for sku in skus if sku.id in json.loads(sku_ids)]

            sku_volumes = {}
            for j in range(1, 100):
                if sheet_plan.cell(j, CELLS['Номенклатура'].column).value in [x.name for x in sku_group]:
                    sku_id = [x.id for x in sku_group if x.name == sheet_plan.cell(j, CELLS['Номенклатура'].column).value][0]
                    volume = abs(excel.evaluate("'{}'!{}".format(
                        SHEETS[1],
                        sheet_plan.cell(j, CELLS['План производства'].column).coordinate)
                    ))
                    sku_volumes[sku_id] = volume

            boiling_weights = []
            if sheet_plan.cell(i, CELLS['Объемы варок'].column).value is not None:
                boiling_weights = re.split(', |. | ', sheet_plan.cell(i, CELLS['Объемы варок'].column).value)
                boiling_weights = [x for x in boiling_weights if BOILING_LIMITS['MIN'] <= x <= BOILING_LIMITS['MAX']]
                boiling_weights = [int(x) for x in boiling_weights if isinstance(x, int) or x.isdigit()]

            if len(boiling_weights) > boilings_count:
                boiling_weights = boilings_count * [BOILING_LIMITS['MAX']]
            else:
                boiling_weights += int(boilings_count - len(boiling_weights)) * [BOILING_LIMITS['MAX']]
            response['Boilings'].append({
                "BoilingId": boiling_id,
                "BoilingCount": boilings_count,
                "BoilingWeights": boiling_weights,
                # "SKUIds": sku_ids,
                "SKUVolumes": sku_volumes

            })

    response['Boilings'] = [x for x in response['Boilings'] if x['BoilingCount'] > 0]
    return response


def build_plan(date, df, request_list):
    filename = '{}_{}.xlsx'.format('plan', date.strftime('%Y-%m-%d'))
    path = '{}/{}'.format('app/data/plan', filename)

    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer, sheet_name=SHEETS[0])
        writer.save()

    wb = openpyxl.load_workbook(filename=path)
    sheet_plan = wb.create_sheet(SHEETS[1])

    # make invisible columns
    sheet_plan.column_dimensions[openpyxl.utils.get_column_letter(COLUMNS['SKUS_ID'])].hidden = True
    sheet_plan.column_dimensions[openpyxl.utils.get_column_letter(COLUMNS['BOILING_ID'])].hidden = True

    # Заполнение первой строки и ее заморозка
    # todo: добавить еще цех и дальнейшую группировку ячеек
    for key in CELLS.keys():
        sheet_plan.cell(CELLS[key].row, CELLS[key].column).value = key
    sheet_plan.freeze_panes = sheet_plan['A2']

    # получаем все форм факторы
    form_factors = set([x["GroupSKU"][0]["SKU"].form_factor for x in request_list])

    # задаем строки, с которых мы бежим вниз
    cur_row, space_rows = 2, 3
    for form_factor in form_factors:
        group_skus = [x for x in request_list if x["GroupSKU"][0]["SKU"].form_factor == form_factor]
        result_row = cur_row

        total_weight_row = (result_row + len(group_skus) + 1)
        group_sku_length = sum([len(x["GroupSKU"]) for x in group_skus])
        colour = COLOURS[group_skus[0]["GroupSKU"][0]["SKU"].form_factor]
        # красим ячейки в нужный цвет
        colour_range(sheet=sheet_plan,
                     start_row=cur_row,
                     end_row=cur_row + group_sku_length,
                     start_col=CELLS['Форм фактор'].column,
                     end_col=CELLS['План производства'].column + 1,
                     colour=colour)

        # Создаем таблицу с итоговыми варками
        sheet_plan.merge_cells(start_row=total_weight_row,
                               start_column=COLUMNS['BoilingVolume'],
                               end_row=total_weight_row,
                               end_column=COLUMNS['BoilingVolume'] + 1)
        sheet_plan.cell(total_weight_row, COLUMNS['BoilingVolume']).value = 'Объем варки'
        sheet_plan.cell(total_weight_row, COLUMNS['BoilingVolume']).fill = PatternFill("solid", fgColor=colour)
        sheet_plan.cell(total_weight_row, CELLS['Расчет'].column).value = group_skus[0]["GroupSKU"][0]["SKU"].output_per_ton
        sheet_plan.cell(total_weight_row, CELLS['Расчет'].column).fill = PatternFill("solid", fgColor=colour)

        # создаем колонку с форм-фактором
        sheet_plan.merge_cells(start_row=cur_row,
                               start_column=CELLS['Форм фактор'].column,
                               end_row=cur_row + group_sku_length - 1,
                               end_column=CELLS['Форм фактор'].column)

        sheet_plan.cell(cur_row, CELLS['Форм фактор'].column).value = group_skus[0]["GroupSKU"][0]["SKU"].form_factor
        sheet_plan.cell(cur_row, CELLS['Форм фактор'].column).alignment = Alignment(horizontal='center', vertical='center')

        for group_sku in group_skus:
            group_formula = []
            # Записываем все в таблицу с SKU
            for sku in group_sku["GroupSKU"]:
                formula_plan = "=INDEX('файл остатки'!$A$5:$DK$265,MATCH($O$1,'файл остатки'!$A$5:$A$228,0),MATCH({},'файл остатки'!$A$5:$DK$5,0))".format(
                    sheet_plan.cell(cur_row, CELLS['Номенклатура'].column).coordinate)
                formula_remains = "=INDEX('файл остатки'!$A$5:$DK$265,MATCH($O$2,'файл остатки'!$A$5:$A$228,0),MATCH({},'файл остатки'!$A$5:$DK$5,0))".format(
                    sheet_plan.cell(cur_row, CELLS['Номенклатура'].column).coordinate)



                sheet_plan.cell(cur_row, CELLS['Бренд'].column).value = sku["SKU"].brand_name
                sheet_plan.cell(cur_row, CELLS['Номенклатура'].column).value = sku["SKU"].name
                sheet_plan.cell(cur_row, CELLS['Факт.остатки, заявка'].column).value = formula_plan
                sheet_plan.cell(cur_row, CELLS['Нормативные остатки'].column).value = formula_remains
                sheet_plan.cell(cur_row, CELLS['План производства'].column).value = '=MIN({}, 0)'\
                    .format(sheet_plan.cell(cur_row, CELLS['Факт.остатки, заявка'].column).coordinate)
                group_formula.append(sheet_plan.cell(cur_row, CELLS['План производства'].column).coordinate)
                cur_row += 1

            # Записываем результат
            sheet_plan.merge_cells(start_row=result_row, start_column=COLUMNS['BoilingVolume'],
                                   end_row=result_row, end_column=COLUMNS['BoilingVolume'] + 1)
            sheet_plan.cell(result_row, COLUMNS['BoilingVolume']).value = '{}% варка, {}, Лактоза {}, Id {}'.format(
                group_sku["GroupSKU"][0]["SKU"].boiling.percent,
                group_sku["GroupSKU"][0]["SKU"].boiling.ferment,
                group_sku["GroupSKU"][0]["SKU"].boiling.is_lactose,
                group_sku["GroupSKU"][0]["SKU"].boiling_id
            )
            formula_boiling_count = '{}'.format(str(group_formula).strip('[]').replace(',', ' +').replace('\'', "").upper())
            sheet_plan.cell(result_row, CELLS['Расчет'].column).value = '=-({}) / {}'.format(
                formula_boiling_count,
                sheet_plan.cell(total_weight_row, CELLS['Расчет'].column).coordinate.upper())
            sheet_plan.cell(result_row, CELLS['План'].column).value = '=ROUND({}, 0)'\
                .format(sheet_plan.cell(result_row, CELLS['Расчет'].column).coordinate)
            sheet_plan.cell(result_row, COLUMNS['SKUS_ID']).value = str([x["SKU"].id for x in group_sku["GroupSKU"]])
            sheet_plan.cell(result_row, COLUMNS['BOILING_ID']).value = group_sku["GroupSKU"][0]["SKU"].boiling_id

            colour_range(sheet_plan,
                         start_row=result_row,
                         end_row=result_row + 1,
                         start_col=COLUMNS['BoilingVolume'],
                         end_col=CELLS['План'].column + 1,
                         colour=colour)

            result_row += 1

        cur_row = max(result_row, cur_row) + space_rows

    # set style
    col = sheet_plan.column_dimensions['A']

    wb.save(path)
    return '{}/{}'.format('data/plan', filename)


def colour_range(sheet, start_row, end_row, start_col, end_col, colour):
    print('Colour {} cells {}'.format(colour, (start_row, end_row, start_col, end_col)))
    for i in range(start_row, end_row):
        for j in range(start_col, end_col):
            sheet.cell(i, j).fill = PatternFill("solid", fgColor=colour)
