import pandas as pd
from datetime import datetime
import openpyxl
from openpyxl.utils import FORMULAE


def build_plan(date, df, request_list):
    filename = '{}_{}.xlsx'.format('plan', date.strftime('%Y-%m-%d'))
    path = '{}/{}'.format('data/plan', filename)

    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer, sheet_name='файл остатки')
        writer.save()

    wb = openpyxl.load_workbook(filename=path)
    sheet_plan = wb.create_sheet('планирование суточное')
    sheet_remains = wb.get_sheet_by_name('файл остатки')

    # Заполнение первой строки и ее заморозка
    # todo: добавить еще цех и дальнейшую группировку ячеек
    sheet_plan.cell(1, 1).value = 'Форм фактор'
    sheet_plan.cell(1, 2).value = 'Бренд'
    sheet_plan.cell(1, 3).value = 'Номенклатура'
    sheet_plan.cell(1, 4).value = 'Факт.остатки, заявка'
    sheet_plan.cell(1, 5).value = 'Нормативные остатки'
    sheet_plan.cell(1, 6).value = 'План производства'
    sheet_plan.cell(1, 12).value = 'Расчет'
    sheet_plan.cell(1, 13).value = 'План'
    sheet_plan['O1'] = 'Фактические остатки на складах - Заявлено, кг:'
    sheet_plan['O2'] = 'Нормативные остатки, кг'
    sheet_plan.freeze_panes = sheet_plan['A2']
    # sheet_plan.freeze_panes(2, 1)

    form_factors = set([x["GroupSKU"][0]["SKU"].form_factor for x in request_list])

    cur_row = 2
    space_rows = 3

    for form_factor in form_factors:
        group_skus = [x for x in request_list if x["GroupSKU"][0]["SKU"].form_factor == form_factor]
        result_row = cur_row

        # Создаем таблицу с итоговыми варками
        total_weight_row = (result_row + len(group_skus) + 1)
        sheet_plan.merge_cells(start_row=total_weight_row, start_column=10,
                               end_row=total_weight_row, end_column=11)
        sheet_plan.cell(total_weight_row, 10).value = 'Объем варки'
        sheet_plan.cell(total_weight_row, 12).value = group_skus[0]["GroupSKU"][0]["SKU"].output_per_ton

        for group_sku in group_skus:
            group_formula = []
            # Записываем все в таблицу с SKU
            for sku in group_sku["GroupSKU"]:
                formula_plan = f"=INDEX('файл остатки'.$A$5:$DK$265,MATCH($O$1,'файл остатки'.$A$5:$A$228,0),MATCH({sheet_plan.cell(cur_row, 3).coordinate},'файл остатки'.$A$5:$DK$5,0))"
                formula_remains = "=INDEX('файл остатки'.$A$5:$DK$265,MATCH($O$2,'файл остатки'.$A$5:$A$228,0),MATCH({},'файл остатки'.$A$5:$DK$5,0))".format(
                    sheet_plan.cell(cur_row, 3).coordinate)

                sheet_plan.cell(cur_row, 1).value = sku["SKU"].form_factor
                sheet_plan.cell(cur_row, 2).value = sku["SKU"].brand_name
                sheet_plan.cell(cur_row, 3).value = sku["SKU"].name
                sheet_plan.cell(cur_row, 4).value = formula_plan
                sheet_plan.cell(cur_row, 5).value = formula_remains
                sheet_plan.cell(cur_row, 6).value = '={}'\
                    .format(sheet_plan.cell(cur_row, 4).coordinate)
                group_formula.append(sheet_plan.cell(cur_row, 4).coordinate)
                cur_row += 1

            # Записываем результат
            sheet_plan.merge_cells(start_row=result_row, start_column=10,
                                   end_row=result_row, end_column=11)
            sheet_plan.cell(result_row, 10).value = '{}% варка'.format(group_sku["GroupSKU"][0]["SKU"].boiling.percent)
            formula_boiling_count = '={}'.format(str(group_formula).strip('[]').replace(',', ' +').replace('\'', "").upper())
            print(formula_boiling_count)
            sheet_plan.cell(result_row, 12).value = formula_boiling_count
            sheet_plan.cell(result_row, 13).value = '=ROUND({})'\
                .format(sheet_plan.cell(result_row, 12).coordinate)
            result_row += 1
        cur_row = max(result_row, cur_row) + space_rows

    wb.save(path)
