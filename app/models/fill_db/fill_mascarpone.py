from ...enum import LineName
import pandas as pd
import json
from app.models import *


def read_params(fn='app/data/params/mascarpone.xlsx'):
    df = pd.read_excel(fn, index_col=0)
    return df


def fill_db():
    fill_fermentators()
    fill_boiling_technologies()
    fill_boilings()
    fill_form_factors()
    fill_sku()


def fill_fermentators():
    line_name = LineName.MASCARPONE
    lines = db.session.query(MascarponeLine).all()
    mascarpone_line = [x for x in lines if x.name == line_name][0]
    for output_ton, name in [[255, 'Big'], [225, 'Small']]:
        fermentator = MascarponeFermentator(
            name=name,
            output_ton=output_ton,
        )
        fermentator.line = mascarpone_line
        db.session.add(fermentator)
    db.session.commit()


def fill_boiling_technologies():
    df = read_params()
    boiling_technologies_columns = ['Прием', 'Нагрев', 'Молочная кислота', 'Сепарирование', 'Процент', 'Вкусовая добавка', 'Вес']
    bt_data = df[boiling_technologies_columns]
    bt_data = bt_data.drop_duplicates().fillna('')
    fermentators = db.session.query(MascarponeFermentator).all()
    for column_name in ['Прием', 'Нагрев', 'Молочная кислота', 'Сепарирование', 'Вес']:
        bt_data[column_name] = bt_data[column_name].apply(lambda x: json.loads(x))
    bt_data = bt_data.to_dict('records')
    for bt in bt_data:
        for i in range(2):
            line_name = LineName.MASCARPONE
            technology = MascarponeBoilingTechnology(
                name=MascarponeBoilingTechnology.create_name(
                    line=line_name,
                    weight=bt['Вес'][i],
                    percent=bt['Процент'],
                    flavoring_agent=bt['Вкусовая добавка']),
                pouring_time=bt['Прием'][i],
                heating_time=bt['Нагрев'][i],
                adding_lactic_acid_time=bt['Молочная кислота'][i],
                separation_time=bt['Сепарирование'][i],
            )
            technology.fermentator = fermentators[i]
            db.session.add(technology)
    db.session.commit()


def fill_boilings():
    df = read_params()
    lines = db.session.query(Line).all()
    bts = db.session.query(MascarponeBoilingTechnology).all()
    columns = ['Вкусовая добавка', 'Процент', 'Линия',
               'Прием', 'Нагрев', 'Молочная кислота', 'Сепарирование', 'Вес']
    b_data = df[columns]
    b_data = b_data.drop_duplicates().fillna('')
    for column_name in ['Прием', 'Нагрев', 'Молочная кислота', 'Сепарирование', 'Вес']:
        b_data[column_name] = b_data[column_name].apply(lambda x: json.loads(x))
    b_data = b_data.to_dict('records')
    for b in b_data:
        for i in range(2):
            line_name = LineName.MASCARPONE
            line_id = [x for x in lines if x.name == LineName.MASCARPONE][0].id
            bt_id = [x for x in bts if (x.pouring_time == b['Прием'][i]) &
                     (x.heating_time == b['Нагрев'][i]) &
                     (x.adding_lactic_acid_time == b['Молочная кислота'][i]) &
                     (x.separation_time == b['Сепарирование'][i]) &
                     (x.name == MascarponeBoilingTechnology.create_name(
                         line=line_name, weight=b['Вес'][i], percent=b['Процент'], flavoring_agent=b['Вкусовая добавка']))][0].id
            boiling = MascarponeBoiling(
                percent=b['Процент'],
                flavoring_agent=b['Вкусовая добавка'],
                weight=b['Вес'][i],
                boiling_technology_id=bt_id,
                line_id=line_id
            )
            db.session.add(boiling)
    db.session.commit()


def fill_form_factors():
    mass_ff = MascarponeFormFactor(name='Масса')
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
    lines = db.session.query(MascarponeLine).all()
    boilings = db.session.query(MascarponeBoiling).all()
    form_factors = db.session.query(MascarponeFormFactor).all()
    groups = db.session.query(Group).all()
    fermentators = db.session.query(MascarponeFermentator).all()
    fermentator_small = [x for x in fermentators if x.name == 'Small'][0]

    columns = ['Название SKU', 'Процент', 'Вкусовая добавка', 'Имя бренда', 'Вес нетто', 'Срок хранения',
               'Коробки', 'Скорость упаковки', 'Линия', 'Название форм фактора']

    sku_data = df[columns]
    sku_data = sku_data.drop_duplicates().fillna('')
    sku_data = sku_data.to_dict('records')
    for sku in sku_data:
        add_sku = MascarponeSKU(
            name=sku['Название SKU'],
            brand_name=sku['Имя бренда'],
            weight_netto=sku['Вес нетто'],
            shelf_life=sku['Срок хранения'],
            packing_speed=60 / sku['Скорость упаковки'] * fermentator_small.output_ton,
            in_box=sku['Коробки'],
        )

        line_name = LineName.MASCARPONE
        add_sku.line = [x for x in lines if x.name == line_name][0]
        add_sku.made_from_boilings = [x for x in boilings if
                   (x.percent == sku['Процент']) &
                   (x.flavoring_agent == sku['Вкусовая добавка']) &
                   (x.line_id == add_sku.line.id)]
        add_sku.group = [x for x in groups if x.name == sku['Название форм фактора']][0]
        add_sku.form_factor = [x for x in form_factors if x.name == 'Масса'][0]
        db.session.add(add_sku)
    db.session.commit()



