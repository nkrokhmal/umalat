from app.interactive_imports import *
import pandas as pd
import numpy as np
from flask import current_app
import math
from copy import deepcopy


def generate_constructor_df_v3(df_copy):
    df = df_copy.copy()
    df['plan'] = df['plan'].apply(lambda x: round(x))
    df['boiling_type'] = df['boiling_id'].apply(lambda boiling_id: cast_boiling(boiling_id).boiling_type)
    # todo: исправить костыль с терками
    df['weight'] = df['sku'].apply(lambda x: x.form_factor.relative_weight if x.group.name != 'Терка' else x.form_factor.relative_weight + 30)
    df['percent'] = df['sku'].apply(lambda x: x.made_from_boilings[0].percent)
    df['is_lactose'] = df['sku'].apply(lambda x: x.made_from_boilings[0].is_lactose)
    df['ferment'] = df['sku'].apply(lambda x: x.made_from_boilings[0].ferment)
    df['form_factor'] = df['sku'].apply(lambda x: x.group.name)

    water, boiling_number = handle_water(df[df['boiling_type'] == 'water'])
    salt, boiling_number = handle_salt(df[df['boiling_type'] == 'salt'], boiling_number=boiling_number + 1)
    result = pd.concat([water, salt])
    result['kg'] = result['plan']
    result['boiling'] = result['boiling_id'].apply(lambda x: cast_boiling(x))
    result['name'] = result['sku'].apply(lambda sku: sku.name)
    result['boiling_name'] = result['boiling'].apply(lambda b: b.to_str())
    result['boiling_volume'] = np.where(result['boiling_type'] == 'salt', 850, 1000)
    result['group'] = result['sku'].apply(lambda sku: sku.form_factor.name)

    result = result[['id', 'boiling_id', 'boiling_name', 'boiling_volume', 'form_factor', 'group', 'name', 'kg', 'tag']]
    return result


def handle_water(df, max_weight=1000, min_weight=1000, boiling_number=1):
    boilings = Boilings(max_weight=max_weight, min_weight=min_weight, boiling_number=boiling_number)
    orders = [(False, 3.3, 'Альче', None),
              (True, 3.3, 'Альче', 'Фиор Ди Латте'),
              (True, 3.3, 'Сакко', 'Фиор Ди Латте'),
              (True, 3.6, 'Альче', 'Фиор Ди Латте'),
              (True, 3.6, 'Альче', 'Чильеджина'),
              (True, 3.3, 'Альче', 'Чильеджина'),
              (True, 3.3, 'Сакко', 'Чильеджина')]
    is_lactose = False
    for order in orders:
        df_filter = df[(df['is_lactose'] == order[0]) &
                       (df['percent'] == order[1]) &
                       (df['ferment'] == order[2]) &
                       (order[3] is None or df['form_factor'] == order[3])]
        df_filter_dict = df_filter.sort_values(by='weight', ascending=False).to_dict('records')
        boilings.add_group(df_filter_dict, is_lactose)
        is_lactose = order[0]
    return pd.DataFrame(boilings.boilings), boilings.boiling_number


def handle_salt(df, max_weight=850, min_weight=850, boiling_number=1):
    boilings = Boilings(max_weight=850, min_weight=850, boiling_number=boiling_number)
    for weight, df_grouped_weight in df.groupby('weight'):
        for boiling_id, df_grouped_boiling_id in df_grouped_weight.groupby('boiling_id'):
            new = True
            for form_factor, df_grouped in df_grouped_boiling_id.groupby('form_factor'):
                boilings.add_group(df_grouped.to_dict('records'), new)
                new = False
    boilings.finish()
    return pd.DataFrame(boilings.boilings), boilings.boiling_number


# todo: logic for min weight
class Boilings:
    def __init__(self, max_weight=1000, min_weight=1000, boiling_number=0):
        self.max_weight = max_weight
        self.min_weight = min_weight
        self.boiling_number = boiling_number
        self.boilings = []
        self.cur_boiling = []

    def cur_sum(self):
        if self.cur_boiling:
            return sum([x['plan'] for x in self.cur_boiling])
        return 0

    def add(self, sku):
        while sku['plan'] > 0:
            remainings = self.max_weight - self.cur_sum()
            boiling_weight = min(remainings, sku['plan'])
            new_boiling = deepcopy(sku)
            new_boiling['plan'] = boiling_weight
            new_boiling['tag'] = 'main'
            new_boiling['id'] = self.boiling_number
            sku['plan'] -= boiling_weight
            self.cur_boiling.append(new_boiling)
            if boiling_weight == remainings:
                self.boilings += self.cur_boiling
                self.boiling_number += 1
                self.cur_boiling = []

    def finish(self):
        if self.cur_boiling:
            self.boilings += self.cur_boiling
            self.boiling_number += 1
            self.cur_boiling = []

    def add_remainings(self):
        if self.cur_boiling:
            self.boilings += self.cur_boiling
            self.boiling_number += 1
            self.cur_boiling = []

    def add_group(self, skus, new=True):
        if new:
            self.add_remainings()
        for sku in skus:
            self.add(sku)


def draw_boiling_names(wb):
    boilings = db.session.query(Boiling).all()
    boiling_names = list(set([x.to_str() for x in boilings]))
    boiling_type_sheet = wb['Типы варок']
    draw_row(boiling_type_sheet, 1, ['-'], font_size=8)
    cur_i = 2
    for boiling_name in boiling_names:
        draw_row(boiling_type_sheet, cur_i, [boiling_name], font_size=8)
        cur_i += 1


def draw_skus(wb, sheet_name, data_sku):
    grouped_skus = data_sku[sheet_name]
    grouped_skus.sort(key=lambda x: x.name, reverse=False)
    sku_sheet_name = '{} SKU'.format(sheet_name)
    sku_sheet = wb[sku_sheet_name]

    draw_row(sku_sheet, 1, ['-', '-'], font_size=8)
    cur_i = 2

    for group_sku in grouped_skus:
        draw_row(sku_sheet, cur_i, [group_sku.name, group_sku.made_from_boilings[0].to_str()], font_size=8)
        cur_i += 1


def draw_constructor_template(df, file_name, wb, df_extra_packing, batch_number=0):
    skus = db.session.query(SKU).all()
    data_sku = {'Вода': [x for x in skus if x.made_from_boilings[0].boiling_type == 'water'],
                'Соль': [x for x in skus if x.made_from_boilings[0].boiling_type == 'salt']}

    draw_boiling_names(wb)
    extra_packing_sheet = wb['Дополнительная фасовка']
    cur_i = 2
    for value in df_extra_packing.values:
        draw_row(extra_packing_sheet, cur_i, value, font_size=8)
        cur_i += 1

    for sheet_name in ['Соль', 'Вода']:
        boiling_sheet = wb[sheet_name]
        draw_skus(wb, sheet_name, data_sku)

        cur_i = 2
        values = []
        sku_names = [x.name for x in data_sku[sheet_name]]
        df_filter = df[df['name'].isin(sku_names)].copy()
        for id, grp in df_filter.groupby('id', sort=False):
            for i, row in grp.iterrows():
                v = []
                v += list(row.values)
                v += ['']
                values.append(v[:-1])
            values.append(['-'] * (len(df_filter.columns) + 1))

        for v in values:
            if v[0] == '-':
                ids = [3, 4, 5, 6, 7, 8, 10, 11]
                for id in ids:
                    draw_cell(boiling_sheet, id, cur_i, v[0], font_size=8)
                    # draw_cell(boiling_sheet, id, cur_i, v[id - 1], font_size=8)
                if sheet_name == 'Вода':
                    first_cell_formula = '=IF(K{0}="-", "", {1} + SUM(INDIRECT(ADDRESS(2,COLUMN(N{0})) & ":" & ADDRESS(ROW(),COLUMN(N{0})))))'.format(
                        cur_i, batch_number)
                else:
                    first_cell_formula = '=IF(K{0}="-", "-", 1 + MAX(\'Вода\'!$A$2:$A$100) + SUM(INDIRECT(ADDRESS(2,COLUMN(N{0})) & ":" & ADDRESS(ROW(),COLUMN(N{0})))))'.format(
                        cur_i)
                draw_cell(boiling_sheet, 1, cur_i, first_cell_formula, font_size=8)

            else:
                if v[-1] == 'main':
                    colour = get_colour_by_name(v[6], skus)
                else:
                    colour = current_app.config['COLOURS']['Remainings']

                if sheet_name == 'Вода':
                    v[0] = '=IF(K{0}="-", "", {1} + SUM(INDIRECT(ADDRESS(2,COLUMN(N{0})) & ":" & ADDRESS(ROW(),COLUMN(N{0})))))'.format(
                        cur_i, batch_number)
                else:
                    v[0] = '=IF(K{0}="-", "-", 1 + MAX(\'Вода\'!$A$2:$A$100) + SUM(INDIRECT(ADDRESS(2,COLUMN(N{0})) & ":" & ADDRESS(ROW(),COLUMN(N{0})))))'.format(
                        cur_i)

                v[1] = '=IF(G{0}="","",IF(K{0}="-","",1+SUM(INDIRECT(ADDRESS(2,COLUMN(N{0}))&":"&ADDRESS(ROW(),COLUMN(N{0}))))))'.format(
                    cur_i)
                draw_row(boiling_sheet, cur_i, v[:-1], font_size=8, color=colour)
                draw_cell(boiling_sheet, 10, cur_i, 1, font_size=8)
            cur_i += 1
    new_file_name = '{} План по варкам'.format(file_name.split(' ')[0])
    path = '{}/{}.xlsx'.format(current_app.config['BOILING_PLAN_FOLDER'], new_file_name)

    wb.active = 0
    wb["Соль"].views.sheetView[0].tabSelected = False
    wb.save(path)
    return '{}.xlsx'.format(new_file_name)


def get_colour_by_name(sku_name, skus):
    sku = [x for x in skus if x.name == sku_name]
    if len(sku) > 0:
        return current_app.config['COLOURS'][sku[0].group.name]
    else:
        return current_app.config['COLOURS']['Default']
