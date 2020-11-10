import pandas as pd
import xlsxwriter
from datetime import datetime
from xlsxwriter.utility import xl_rowcol_to_cell


def build_plan(date, df, request_list):
    filename = '{}_{}.xlsx'.format('plan', date.strftime('%Y-%m-%d'))
    path = '{}/{}'.format('data/plan', filename)

    writer = pd.ExcelWriter(path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='файл остатки')
    pd.DataFrame().to_excel(writer, sheet_name='планирование суточное')

    sheet_plan = writer.sheets['планирование суточное']

    # Заполнение первой строки и ее заморозка
    # todo: добавить еще цех и дальнейшую группировку ячеек
    sheet_plan.write(0, 0, 'Форм фактор')
    sheet_plan.write(0, 1, 'Бренд')
    sheet_plan.write(0, 2, 'Номенклатура')
    sheet_plan.write(0, 3, 'Факт.остатки, заявка')
    sheet_plan.write(0, 4, 'Нормативные остатки')
    sheet_plan.write(0, 5, 'План производства')
    sheet_plan.write(0, 11, 'Расчет')
    sheet_plan.write(0, 12, 'План')
    sheet_plan.write('O1', 'Фактические остатки на складах - Заявлено, кг:')
    sheet_plan.write('O2', 'Нормативные остатки, кг')
    sheet_plan.freeze_panes(1, 0)

    form_factors = set([x["GroupSKU"][0]["SKU"].form_factor for x in request_list])

    cur_row = 1
    space_rows = 3

    for form_factor in form_factors:
        group_skus = [x for x in request_list if x["GroupSKU"][0]["SKU"].form_factor == form_factor]
        result_row = cur_row
        for group_sku in group_skus:
            # Записываем вес продукта с одной варки
            total_weight_row = (result_row + len(group_sku) + 1)
            # sheet.write(total_weight_row, 9, 'Объем варки')
            sheet_plan.merge_range(first_row=total_weight_row, first_col=9,
                              last_row=total_weight_row, last_col=10,
                              data='Объем варки')
            sheet_plan.write(total_weight_row, 11, group_sku["GroupSKU"][0]["SKU"].output_per_ton)

            group_formula = []
            # Записываем все в таблицу с SKU
            for sku in group_sku["GroupSKU"]:
                formula_plan = '=INDEX($\'файл остатки\'.$A$5:$DK$265,MATCH($O$1,$\'файл остатки\'.$A$5:$A$228,0),MATCH({},$\'файл остатки\'.$A$5:$DK$5,0))'.format(xl_rowcol_to_cell(cur_row, 2))
                formula_remains = "=INDEX($'файл остатки'.$A$5:$DK$265,MATCH($O$2,$'файл остатки'.$A$5:$A$228,0),MATCH({},$'файл остатки'.$A$5:$DK$5,0))".format(xl_rowcol_to_cell(cur_row, 2))

                sheet_plan.write(cur_row, 0, sku["SKU"].form_factor)
                sheet_plan.write(cur_row, 1, sku["SKU"].brand_name)
                sheet_plan.write(cur_row, 2, sku["SKU"].name)
                sheet_plan.write(cur_row, 3, formula_plan)
                sheet_plan.write_formula(cur_row, 4, formula_remains)
                sheet_plan.write_formula(cur_row, 5, '={}'.format(xl_rowcol_to_cell(cur_row, 3)))
                group_formula.append(xl_rowcol_to_cell(cur_row, 3))
                cur_row += 1

            # Записываем результат
            # sheet.write(result_row, 9, '{}% варка'.format(group_sku["GroupSKU"][0].boiling.percent))

            sheet_plan.merge_range(first_row=result_row, first_col=9,
                              last_row=result_row, last_col=10,
                              data='{}% варка'.format(group_sku["GroupSKU"][0]["SKU"].boiling.percent))
            formula_boiling_count = '={}'.format(str(group_formula).strip('[]').replace(',', '+'))
            sheet_plan.write_formula(result_row, 11, formula_boiling_count)
            sheet_plan.write_formula(result_row, 12, '=ROUND({})'.format(xl_rowcol_to_cell(result_row, 11)))
            result_row += 1
        cur_row = max(result_row, cur_row) + space_rows

    # workbook.close()
    writer.save()







