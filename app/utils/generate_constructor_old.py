from app.interactive_imports import *
import pandas as pd
import numpy as np
from flask import current_app
import math
from copy import deepcopy


def generate_constructor_df_v2(df):
    values = []
    generate_constructor_df_v3(df)
    df['boiling_type'] = df['boiling_id'].apply(lambda boiling_id: cast_boiling(boiling_id).boiling_type)
    df['weight'] = df['sku'].apply(lambda x: x.boiling_form_factors[0].weight)
    df['_sorting_key'] = np.where(df['boiling_type'] == 'salt', df['weight'], -df['weight'])
    df = df.sort_values(by='_sorting_key')
    df.pop('_sorting_key')

    # todo: haddcode
    boiling_grp_df = pd.DataFrame(remove_duplicates(df['boiling_id'].values), columns=['boiling_id'])
    boiling_grp_df['n_chiledzhina'] = boiling_grp_df['boiling_id'].apply(lambda boiling_id: df[
        (df['boiling_id'] == boiling_id) & (
            df['sku'].apply(lambda sku: sku.form_factor.name).str.contains('Чильеджина'))]['plan'].sum())
    boiling_grp_df = boiling_grp_df.sort_values(by='n_chiledzhina')

    for boiling_id in boiling_grp_df['boiling_id'].values:
        boiling_grp = df[df['boiling_id'] == boiling_id]
        volume = boiling_grp['sku'].iloc[0].boilings[0].cheese_types.output

        boiling_dic = OrderedDict()
        for i, row in boiling_grp.iterrows():
            boiling_dic[cast_sku(row['sku_id'])] = row['plan']

        total_kg = sum(boiling_dic.values())
        total_kg = custom_round(total_kg, volume, rounding='ceil')

        # n_boilings = int(total_kg / volume)
        n_boilings = math.ceil(total_kg / volume)
        for i in range(n_boilings):
            cur_kg = volume

            boiling_request = OrderedDict()
            for k, v in list(boiling_dic.items()):
                boil_kg = min(cur_kg, boiling_dic[k])

                boiling_dic[k] -= boil_kg
                cur_kg -= boil_kg

                if k not in boiling_request:
                    boiling_request[k] = 0
                boiling_request[k] += boil_kg

                if cur_kg == 0:
                    break

            if cur_kg != 0:
                print('Non-zero')
                k = [k for k, v in boiling_request.items() if v != 0][0]
                boiling_request[k] += cur_kg

            boiling_request = [[k, v] for k, v in boiling_request.items() if v != 0]
            values.append([boiling_id, boiling_request])

    df = pd.DataFrame(values, columns=['boiling_id', 'boiling_request'])
    df['boiling_id'] = df['boiling_id'].astype(str)
    df['boiling_type'] = df['boiling_id'].apply(lambda boiling_id: cast_boiling(boiling_id).boiling_type)
    df['used'] = False

    df['boiling_label'] = df['boiling_id'].apply(
        lambda boiling_id: '{} {}{}'.format(cast_boiling(boiling_id).percent,
                                            cast_boiling(boiling_id).ferment,
                                            '' if cast_boiling(boiling_id).is_lactose else ' без лактозы'))

    df['volume'] = df['boiling_request'].apply(lambda req: sum([v for k, v in req]))

    df['boiling_request'] = df['boiling_request'].apply(
        lambda req: [[cast_sku(k), round(v)] for k, v in req if v != 0])

    values = []
    for i, row in df.iterrows():
        for sku, kg in row['boiling_request']:
            values.append([i + 1, cast_boiling(row['boiling_id']), sku, kg])

    boiling_plan_df = pd.DataFrame(values, columns=['id', 'boiling', 'sku', 'kg'])
    boiling_plan_df['weight'] = boiling_plan_df['sku'].apply(lambda x: x.boiling_form_factors[0].weight)
    return boiling_plan_df


def generate_constructor_df(df):
    result = []
    for boiling_id, boiling_grp in df.groupby('boiling_id'):
        boiling_grp['weight'] = boiling_grp['sku'].apply(lambda x: x.boiling_form_factors[0].weight)
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
        min_boiling_weight = min([x['weight'] for x in boiling])
        max_boiling_weight = max([x['weight'] for x in boiling])
        for boiling_element in boiling:
            full_result.append({
                'id': i,
                'boiling': boiling_element['sku'].boilings[0],
                'sku': boiling_element['sku'],
                'kg': boiling_element['plan'],
                'min_weight': min_boiling_weight,
                'max_weight': max_boiling_weight
            })
    boiling_plan_df = pd.DataFrame(full_result)
    boiling_plan_df = boiling_plan_df.sort_values(by=['min_weight', 'max_weight', 'id'])
    return boiling_plan_df


def generate_full_constructor_df(boiling_plan_df):
    # create dataframe for samples
    df = boiling_plan_df.copy()
    df['name'] = df['sku'].apply(lambda sku: sku.name)
    # todo: make properly
    df['boiling_name'] = df['boiling'].apply(
        lambda b: '{} {} {}'.format(b.percent, b.ferment, '' if b.is_lactose else 'без лактозы'))
    # todo: make properly
    df['boiling_volume'] = np.where(df['boiling_name'].str.contains('2.7'), 850, 1000)
    df['form_factor'] = df['sku'].apply(lambda sku: sku.form_factor.name)
    df['boiling_id'] = df['boiling'].apply(lambda b: b.id)
    df = df[['id', 'boiling_id', 'boiling_name', 'boiling_volume', 'form_factor', 'name', 'kg']]
    # df = df.sort_values(by=['boiling_id', 'id', 'boiling_name', 'form_factor', 'name'])
    return df.reset_index(drop=True)


def generate_empty_sku():
    values = db.session.query(SKU).all()
    skus = pd.DataFrame(values, columns=['sku'])
    skus['boiling'] = skus['sku'].apply(lambda sku: sku.boilings[0])
    skus['id'] = ''
    skus['kg'] = 0
    skus = skus[['id', 'boiling', 'sku', 'kg']]
    return skus


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
                 ['id варки', "Номер варки", 'Тип варки', 'Объем варки', 'Форм фактор', 'SKU', 'КГ', 'Остатки',
                  'Разделитель'],
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
            formula_remains = '=IF(M{0} - INDIRECT("M" & ROW() - 1) = 0, "", INDIRECT("M" & ROW() - 1) - M{0})'.format(
                cur_i)
            formula_calc = '=IF(I{0} = "-", -INDIRECT("D" & ROW() - 1),G{0})'.format(cur_i)
            formula_remains_cumsum = '=IF(I{0} = "-", SUM(INDIRECT(ADDRESS(2,COLUMN(J{0})) & ":" & ADDRESS(ROW(),COLUMN(J{0})))), 0)'.format(
                cur_i)
            formula_delimiter_int = '=IF(I{0}="-",1,0)'.format(cur_i)
            formula_zeros = '=IF(K{0} = 0, INDIRECT("M" & ROW() - 1), K{0})'.format(cur_i)

            v[
                1] = '=IF(I{0}="-", "", 1 + SUM(INDIRECT(ADDRESS(2,COLUMN(L{0})) & ":" & ADDRESS(ROW(),COLUMN(L{0})))))'.format(
                cur_i)
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