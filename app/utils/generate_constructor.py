from app.interactive_imports import *
import pandas as pd
import numpy as np
from flask import current_app


def generate_constructor_df(df):
    result = []
    for boiling_id, boiling_grp in df.groupby('boiling_id'):
        boiling_grp['weight'] = boiling_grp['sku'].apply(lambda x: x.weight_netto)
        boiling_volume = boiling_grp['sku'].iloc[0].boilings[0].cheese_types.output

        boiling = 1
        while boiling is not None:
            boiling_grp, boiling = iteration(boiling_grp, boiling_volume)
            if boiling is not None:
                result.append(boiling)
        if (boiling_grp['plan'].sum() > 0):
            result.append(boiling_grp.to_dict('records'))

    full_result = []
    for i, boiling in enumerate(result):
        for boiling_element in boiling:
            full_result.append({
                'id': i,
                'boiling': boiling_element['sku'].boilings[0],
                'sku': boiling_element['sku'],
                'kg': boiling_element['plan']
            })
    return pd.DataFrame(full_result)


def generate_full_constructor_df(boiling_plan_df):
    # create dataframe for samples
    df = boiling_plan_df.copy()
    df['name'] = df['sku'].apply(lambda sku: sku.name)
    # todo: make properly
    df['boiling_name'] = df['boiling'].apply(lambda b: '{} {} {}'.format(b.percent, b.ferment, '' if b.is_lactose else 'без лактозы'))
    # todo: make properly
    df['boiling_volume'] = np.where(df['boiling_name'].str.contains('2.7'), 850, 1000)
    df['form_factor'] = df['sku'].apply(lambda sku: sku.form_factor.name)
    df['boiling_id'] = df['boiling'].apply(lambda b: b.id)
    df = df[['id', 'boiling_id', 'boiling_name','boiling_volume','form_factor', 'name', 'kg']]
    df = df.sort_values(by=['boiling_id', 'id', 'boiling_name', 'form_factor', 'name'])
    return df.reset_index(drop=True)


def generate_empty_sku():
    values = db.session.query(SKU).all()
    skus = pd.DataFrame(values, columns=['sku'])
    skus['boiling'] = skus['sku'].apply(lambda sku: sku.boilings[0])
    skus['id'] = ''
    skus['kg'] = 0
    skus = skus[['id', 'boiling', 'sku', 'kg']]
    return skus


def draw_constructor_template(df, file_name, wb):
    skus = db.session.query(SKU).all()
    data_sku = {'Вода': [x.name for x in skus if x.boilings[0].cheese_types.name == 'Вода'],
                'Соль': [x.name for x in skus if x.boilings[0].cheese_types.name == 'Соль']}

    for sheet_name in ['Соль', 'Вода']:
        sku_names = data_sku[sheet_name]
        sku_sheet_name = '{} SKU'.format(sheet_name)
        boiling_sheet = wb[sheet_name]
        sku_sheet = wb[sku_sheet_name]

        draw_row(sku_sheet, 1, ['-'], font_size=8)
        cur_i = 2

        for sku_name in sku_names:
            draw_row(sku_sheet, cur_i, [sku_name], font_size=8)
            cur_i += 1

        cur_i = 2
        values = []
        df_filter = df[df['name'].isin(sku_names)].copy()

        for id, grp in df_filter.groupby('id'):
            for i, row in grp.iterrows():
                v = []
                v += list(row.values)
                v += ['']
                values.append(v[:-1])
            values.append(['-'] * (len(df_filter.columns) + 2))

        for v in values:
            if v[0] == '-':
                ids = [1, 3, 4, 5, 6, 7, 9]
                for id in ids:
                    draw_cell(boiling_sheet, id, cur_i, v[id - 1], font_size=8)
            else:
                colour = get_colour_by_name(v[5], skus)
                v[1] = '=IF(I{0}="-", "", 1 + SUM(INDIRECT(ADDRESS(2,COLUMN(L{0})) & ":" & ADDRESS(ROW(),COLUMN(L{0})))))'.format(
                    cur_i)
                draw_row(boiling_sheet, cur_i, v, font_size=8, color=colour)
            cur_i += 1

    path = '{}/{}.xlsx'.format(current_app.config['BOILING_PLAN_FOLDER'], os.path.splitext(file_name)[0])
    wb.save(path)
    return '{}.xlsx'.format(os.path.splitext(file_name)[0])


def draw_constructor(df, file_name):
    wb = init_sheets('Соль', 'Вода')

    skus = db.session.query(SKU).all()
    data_sku = {'Вода': [x.name for x in skus if x.boilings[0].cheese_types.name == 'Вода'],
                'Соль': [x.name for x in skus if x.boilings[0].cheese_types.name == 'Соль']}

    for sheet_name in ['Соль', 'Вода']:
        sku_names = data_sku[sheet_name]
        sheet = wb[sheet_name]
        for i, v in enumerate([15, 15, 15, 15, 15, 50, 15], 1):
            sheet.column_dimensions[get_column_letter(i)].width = v

        cur_i = 1
        draw_row(sheet, cur_i,
                 ['id варки', "Номер варки", 'Тип варки', 'Объем варки', 'Форм фактор', 'SKU', 'КГ', 'Остатки', 'Разделитель'],
                 font_size=8)
        cur_i += 1

        values = []
        df_filter = df[df['name'].isin(sku_names)].copy()
        for id, grp in df_filter.groupby('id'):
            for i, row in grp.iterrows():
                v = []
                v += list(row.values)
                v += ['']
                values.append(v)

            # add separator
            values.append(['-'] * (len(df_filter.columns) + 1))

        sheet.column_dimensions['A'].hidden = True
        sheet.column_dimensions['I'].hidden = True
        sheet.column_dimensions['J'].hidden = True
        sheet.column_dimensions['K'].hidden = True
        sheet.column_dimensions['L'].hidden = True
        sheet.column_dimensions['M'].hidden = True

        # todo: column names to config
        for v in values:
            formula_remains = '=IF(M{0} - INDIRECT("M" & ROW() - 1) = 0, "", INDIRECT("M" & ROW() - 1) - M{0})'.format(cur_i)
            formula_calc = '=IF(I{0} = "-", -INDIRECT("D" & ROW() - 1),G{0})'.format(cur_i)
            formula_remains_cumsum = '=IF(I{0} = "-", SUM(INDIRECT(ADDRESS(2,COLUMN(J{0})) & ":" & ADDRESS(ROW(),COLUMN(J{0})))), 0)'.format(cur_i)
            formula_delimiter_int = '=IF(I{0}="-",1,0)'.format(cur_i)
            formula_zeros = '=IF(K{0} = 0, INDIRECT("M" & ROW() - 1), K{0})'.format(cur_i)

            v[1] = '=IF(I{0}="-", "", 1 + SUM(INDIRECT(ADDRESS(2,COLUMN(L{0})) & ":" & ADDRESS(ROW(),COLUMN(L{0})))))'.format(cur_i)
            v.insert(-1, formula_remains)
            v.append(formula_calc)
            v.append(formula_remains_cumsum)
            v.append(formula_delimiter_int)
            v.append(formula_zeros)

            colour = get_colour_by_name(v[5], skus)
            draw_row(sheet, cur_i, v, font_size=8, color=colour)
            cur_i += 1

        cur_i += 1
        skus_df = generate_full_constructor_df(generate_empty_sku())
        skus_df = skus_df[skus_df['name'].isin(sku_names)]
        values = []
        for boiling_name, grp1 in skus_df.groupby('boiling_name'):
            for form_factor, grp2 in grp1.groupby('form_factor'):
                for i, row in grp2.iterrows():
                    values.append(list(row.values))

        for v in values:
            colour = get_colour_by_name(v[5], skus)
            draw_row(sheet, cur_i, v, font_size=8, color=colour)
            cur_i += 1

    path = '{}/{}.xlsx'.format(current_app.config['BOILING_PLAN_FOLDER'], os.path.splitext(file_name)[0])
    wb.save(path)
    return '{}.xlsx'.format(os.path.splitext(file_name)[0])


def iteration(df, volume):
    full_boilings = df[df['plan'] > volume]
    if full_boilings.shape[0] > 0:
        new_boiling = full_boilings.iloc[0].to_dict()
        new_boiling['plan'] = volume
        df['plan'].loc[df['sku'] == new_boiling['sku']] -= volume
        return df, [new_boiling]

    for weight, boiling_grp in df.groupby('weight'):
        if boiling_grp['plan'].sum() > volume:
            boiling_grp = boiling_grp.sort_values(by='plan', ascending=False).to_dict('records')
            new_boiling = []
            cur_weight = 0
            for b_grp in boiling_grp:
                if cur_weight + b_grp['plan'] < volume:
                    new_boiling.append(b_grp)
                    df['plan'].loc[df['sku'] == b_grp['sku']] = 0
                    cur_weight += b_grp['plan']
                else:
                    b_grp['plan'] = volume - cur_weight
                    new_boiling.append(b_grp)
                    df['plan'].loc[df['sku'] == b_grp['sku']] -= volume - cur_weight
                    return df, new_boiling
    df = df[df['plan'] > 0]
    new_boiling = []
    cur_weight = 0
    for data in df.sort_values(by='weight').to_dict('records'):
        if cur_weight + data['plan'] < volume:
            new_boiling.append(data)
            df['plan'].loc[df['sku'] == data['sku']] = 0
            cur_weight += data['plan']
        else:
            data['plan'] = volume - cur_weight
            new_boiling.append(data)
            df['plan'].loc[df['sku'] == data['sku']] -= volume - cur_weight
            return df, new_boiling
    return df, None


def get_colour_by_name(sku_name, skus):
    sku = [x for x in skus if x.name == sku_name]
    if len(sku) > 0:
        return current_app.config['COLOURS'][sku[0].form_factor.name]
    else:
        return current_app.config['COLOURS']['Default']
