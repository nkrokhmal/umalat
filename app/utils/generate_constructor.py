from app.interactive_imports import *
import pandas as pd
import numpy as np


def generate_constructor_df(df):
    values = []
    for boiling_id, boiling_grp in df.groupby(0):
        boiling_dic = boiling_grp[[1, 2]].set_index(1).to_dict(orient='index')
        boiling_dic = {k: v[2] for k, v in boiling_dic.items()}
        boiling_dic = {cast_sku(k): v for k, v in boiling_dic.items()}
        total_kg = sum(boiling_dic.values())

        # round to get full
        # todo: proper logic
        boiling_type = 'salt' if str(cast_boiling(boiling_id).percent) == '2.7' else 'water'
        volume = 1000 if boiling_type == 'water' else 850

        total_kg = custom_round(total_kg, volume, rounding='floor')

        n_boilings = int(total_kg / volume)
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
    df['boiling_type'] = df['boiling_id'].apply(
        lambda boiling_id: 'salt' if str(cast_boiling(boiling_id).percent) == '2.7' else 'water')
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


def draw_constructor(df):
    wb = init_sheets('Соль', 'Вода')

    skus = db.session.query(SKU).all()
    data_sku = {}
    # data_sku['Вода'] = [x.name for x in skus if x.boilings[0].percent  ]
    for sheet_name in ['Вода', 'План']:

        sheet = wb[sheet_name]
        for i, v in enumerate([15, 15, 15, 15, 15, 50, 15], 1):
            sheet.column_dimensions[get_column_letter(i)].width = v

        cur_i = 1
        draw_row(sheet, cur_i,
                 ['id варки', "Номер варки", 'Тип варки', 'Объем варки', 'Форм фактор', 'SKU', 'КГ', 'Разделитель'],
                 font_size=8)
        cur_i += 1

        values = []
        for id, grp in df.groupby('id'):
            for i, row in grp.iterrows():
                v = []
                v += list(row.values)
                v += ['']
                values.append(v)

            # add separator
            values.append(['-'] * (len(df.columns) + 1))

        for v in values:
            draw_row(sheet, cur_i, v, font_size=8)
            cur_i += 1

        cur_i += 1
        skus = generate_full_constructor_df(generate_empty_sku())
        values = []
        for boiling_name, grp1 in skus.groupby('boiling_name'):
            for form_factor, grp2 in grp1.groupby('form_factor'):
                for i, row in grp2.iterrows():
                    values.append(list(row.values))

        for v in values:
            draw_row(sheet, cur_i, v, font_size=8)
            cur_i += 1

    wb.save('app/data/tmp/constructor.xlsx')