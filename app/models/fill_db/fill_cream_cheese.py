from ...enum import LineName
import pandas as pd
import json
from app.models import *


def read_params(fn='app/data/params/creamcheese.xlsx'):
    df = pd.read_excel(fn, index_col=0)
    return df


def fill_db():
    fill_boiling_technologies()
    fill_boilings()
    fill_form_factors()
    fill_sku()


def fill_boiling_technologies():
    df = read_params()
    boiling_technologies_columns = ['Охлаждение', 'Сепарирование', 'Посолка', 'П', 'Процент']
    bt_data = df[boiling_technologies_columns]
    bt_data = bt_data.drop_duplicates()
    bt_data = bt_data.to_dict('records')
    for bt in bt_data:
        line_name = LineName.MASCARPONE
        technology = CreamCheeseBoilingTechnology(
            name=CreamCheeseBoilingTechnology.create_name(
                line=line_name,
                percent=bt['Процент']),
            cooling_time=bt['Охлаждение'],
            separation_time=bt['Сепарирование'],
            salting_time=bt['Посолка'],
            p_time=bt['П'],
        )

        db.session.add(technology)
        db.session.commit()


def fill_boilings():
    df = read_params()
    lines = db.session.query(Line).all()
    bts = db.session.query(CreamCheeseBoilingTechnology).all()
    columns = ['Процент', 'Линия', 'Охлаждение', 'Сепарирование', 'Посолка', 'П',]
    b_data = df[columns]
    b_data = b_data.drop_duplicates()
    b_data = b_data.to_dict('records')
    for b in b_data:
        line_name = LineName.MASCARPONE
        line_id = [x for x in lines if x.name == line_name][0].id
        bt_id = [x for x in bts if (x.cooling_time == b['Охлаждение']) &
                 (x.separation_time == b['Сепарирование']) &
                 (x.salting_time == b['Посолка']) &
                 (x.p_time == b['П']) &
                 (x.name == CreamCheeseBoilingTechnology.create_name(
                     line=line_name, percent=b['Процент']))][0].id
        boiling = CreamCheeseBoiling(
            percent=b['Процент'],
            boiling_technology_id=bt_id,
            line_id=line_id
        )
        db.session.add(boiling)
        db.session.commit()


def fill_form_factors():
    mass_ff = CreamCheeseFormFactor(name='Масса')
    db.session.add(mass_ff)
    db.session.commit()


def _cast_non_nan(obj):
    if obj is None:
        return
    elif np.isnan(obj):
        return
    else:
        return obj


def fill_sku():
    df = read_params()
    lines = db.session.query(Line).all()
    boilings = db.session.query(CreamCheeseBoiling).all()
    form_factors = db.session.query(CreamCheeseFormFactor).all()
    groups = db.session.query(Group).all()

    columns = ['Название SKU', 'Процент', 'Имя бренда', 'Вес нетто', 'Срок хранения',
               'Коробки', 'Скорость упаковки', 'Линия', 'Вес форм фактора', 'Название форм фактора']

    sku_data = df[columns]
    sku_data = sku_data.drop_duplicates()
    sku_data = sku_data.to_dict('records')
    for sku in sku_data:
        add_sku = CreamCheeseSKU(
            name=sku['Название SKU'],
            brand_name=sku['Имя бренда'],
            weight_netto=sku['Вес нетто'],
            shelf_life=sku['Срок хранения'],
            packing_speed=sku['Скорость упаковки'],
            in_box=sku['Коробки'],
        )

        line_name = LineName.MASCARPONE
        add_sku.line = [x for x in lines if x.name == line_name][0]

        add_sku.made_from_boilings = [x for x in boilings if
                   (x.percent == sku['Процент']) &
                   (x.line_id == add_sku.line.id)]
        add_sku.group = [x for x in groups if x.name == sku['Название форм фактора']][0]
        add_sku.form_factor = [x for x in form_factors if x.name == 'Масса'][0]
        db.session.add(add_sku)
    db.session.commit()



