from app.interactive_imports import *
import pandas as pd
import numpy as np
from flask import current_app

# todo: вынести цвета в конфиг
COLOURS = {
    'Для пиццы': '#E5B7B6',
    'Моцарелла': '#DAE5F1',
    'Фиор Ди Латте': '#CBC0D9',
    'Чильеджина': '#E5DFEC',
    'Качокавалло': '#F1DADA',
    'Сулугуни': '#F1DADA',
    'Default': '#FFFFFF'
}

def generate_constructor_df(df):
    values = []
    cur_id = 1
    for boiling_id, boiling_grp in df.groupby('boiling_id'):

        # create sku_plan as dict
        sku_plan = OrderedDict() # {sku: kg}
        for i, row in boiling_grp[['sku', 'plan']].iterrows():
            if row['sku'] not in sku_plan:
                sku_plan[row['sku']] = 0
            sku_plan[row['sku']] += row['plan']

        total_kg = sum(sku_plan.values())

        # round to get full
        boiling_type = 'salt' if str(cast_boiling(boiling_id).lines.name) == 'Пицца чиз' else 'water'
        # todo: take from db
        volume = 1000 if boiling_type == 'water' else 850

        total_kg = custom_round(total_kg, volume, rounding='ceil')
        n_boilings = int(total_kg / volume)

        for i in range(n_boilings):
            cur_kg = volume

            boiling_contents = OrderedDict()
            for sku, kg in list(sku_plan.items()):
                boil_kg = min(cur_kg, sku_plan[sku])

                sku_plan[sku] -= boil_kg
                cur_kg -= boil_kg

                if sku not in boiling_contents:
                    boiling_contents[sku] = 0
                boiling_contents[sku] += boil_kg

                if cur_kg == 0:
                    break

            if cur_kg != 0:
                print('Non-zero', sku, kg, cur_kg)
                sku = [k for k, v in boiling_contents.items() if v != 0][0]
                boiling_contents[sku] += cur_kg

            for sku, kg in boiling_contents.items():
                values.append([cur_id, cast_boiling(boiling_id), sku, kg])
            cur_id += 1

    boiling_plan_df = pd.DataFrame(values, columns=['id', 'boiling', 'sku', 'kg'])
    return boiling_plan_df


def generate_full_constructor_df(boiling_plan_df):
    # create dataframe for samples
    df = boiling_plan_df.copy()
    df['name'] = df['sku'].apply(lambda sku: sku.name)
    # todo: make properly
    df['boiling_name'] = df['boiling'].apply(lambda b: '{} {} {}'.format(b.percent, b.ferment, '' if b.is_lactose else 'без лактозы'))
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
                 ['id варки', "Номер варки", 'Тип варки', 'Объем варки', 'Форм фактор', 'SKU', 'КГ', 'Разделитель'],
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

        # todo: column names to config
        for v in values:
            sheet.column_dimensions['J'].hidden = True
            sheet.column_dimensions['K'].hidden = True
            sheet.column_dimensions['L'].hidden = True
            sheet.column_dimensions['M'].hidden = True

            formula_remains = '=IF({0}{1} - {0}{2} = 0, "", {0}{1} - {0}{2})'.format('M', cur_i, cur_i - 1)
            formula_calc = '=IF({0}{3} = "-", -{1}{4},{2}{3})'.format('I', 'D', 'G', cur_i, cur_i - 1)
            formula_remains_cumsum = '=IF({0}{2} = "-", SUM({1}$2:J{2}), 0)'.format('I', 'J', cur_i, cur_i - 1)
            formula_delimiter_int = '=IF({0}{1}="-",1,0)'.format('I', cur_i)
            formula_zeros = '=IF({0}{2} = 0, {1}{3}, {0}{2})'.format('K', 'M', cur_i, cur_i - 1)

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

    path = '{}/{}.xlsx'.format(current_app.config['CONSTRUCTOR_FOLDER'], os.path.splitext(file_name)[0])
    link = '{}/{}.xlsx'.format(current_app.config['CONSTRUCTOR_LINK_FOLDER'], os.path.splitext(file_name)[0])
    wb.save(path)
    return link


def get_colour_by_name(sku_name, skus):
    sku = [x for x in skus if x.name == sku_name]
    if len(sku) > 0:
        return COLOURS[sku[0].form_factor.name]
    else:
        return COLOURS['Default']
