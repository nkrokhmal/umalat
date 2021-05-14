from ...enum import LineName
import pandas as pd
import json
from app.models import *


def read_params(fn="app/data/static/params/mascarpone.xlsx"):
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
    for i, name in enumerate([
        "Big", "Small", "Small", "Small", "Small", "Small", "Small",
    ]):
        fermentator = MascarponeSourdough(
            number=i+1,
            name=name,
        )
        fermentator.line = mascarpone_line
        db.session.add(fermentator)
    db.session.commit()


def fill_boiling_technologies():
    df = read_params()
    boiling_technologies_columns = [
        "Название форм фактора",
        "Прием",
        "Нагрев",
        "Молочная кислота",
        "Сепарирование",
        "Внесение ингредиентов",
        "Процент",
        "Вкусовая добавка",
        "Вес",
        "Выход",
    ]
    bt_data = df[boiling_technologies_columns]
    bt_data = bt_data.drop_duplicates().fillna("")
    fermentators = db.session.query(MascarponeSourdough).all()
    big_fermentators = [x for x in fermentators if x.name == "Big"]
    small_fermentators = [x for x in fermentators if x.name == "Small"]
    fermentators_dict = {
        0: big_fermentators,
        1: small_fermentators,
    }

    for column_name in ["Прием", "Нагрев", "Молочная кислота", "Сепарирование", "Вес", "Выход"]:
        bt_data[column_name] = bt_data[column_name].apply(lambda x: json.loads(x))
    bt_data = bt_data.to_dict("records")
    for bt in bt_data:
        n = 1 if bt["Название форм фактора"] == "Сливки" else 2
        for i in range(n):
            line_name = LineName.MASCARPONE
            technology = MascarponeBoilingTechnology(
                name=MascarponeBoilingTechnology.create_name(
                    line=line_name,
                    weight=bt["Вес"][i],
                    percent=bt["Процент"],
                    flavoring_agent=bt["Вкусовая добавка"],
                ),
                pouring_time=bt["Прием"][i],
                heating_time=bt["Нагрев"][i],
                adding_lactic_acid_time=bt["Молочная кислота"][i],
                pumping_off_time=bt["Сепарирование"][i],
                ingredient_time=bt["Внесение ингредиентов"],
                weight=bt["Вес"][i],
                output_ton=bt["Выход"][i],
            )
            if "Сливки" not in bt["Название форм фактора"]:
                technology.sourdoughs = fermentators_dict[i]
            db.session.add(technology)
    db.session.commit()


def fill_boilings():
    df = read_params()
    lines = db.session.query(Line).all()
    bts = db.session.query(MascarponeBoilingTechnology).all()
    columns = [
        "Вкусовая добавка",
        "Процент",
        "Линия",
        "Вес",
        "Коэффициент",
    ]
    b_data = df[columns]
    b_data = b_data.drop_duplicates().fillna("")
    for column_name in ["Вес"]:
        b_data[column_name] = b_data[column_name].apply(lambda x: json.loads(x))
    b_data = b_data.to_dict("records")
    for b in b_data:
        bts_name = []
        for i in range(2):
            line_name = LineName.MASCARPONE
            line_id = [x for x in lines if x.name == LineName.MASCARPONE][0].id
            bts_name += [
                x
                for x in bts if
                (
                    x.name
                    == MascarponeBoilingTechnology.create_name(
                        line=line_name,
                        weight=b["Вес"][i],
                        percent=b["Процент"],
                        flavoring_agent=b["Вкусовая добавка"],
                    )
                )
            ]
        boiling = MascarponeBoiling(
            percent=b["Процент"],
            flavoring_agent=b["Вкусовая добавка"],
            boiling_technologies=bts_name,
            output_coeff=b["Коэффициент"],
            line_id=line_id,
        )
        db.session.add(boiling)
    db.session.commit()


def fill_form_factors():
    mass_ff = MascarponeFormFactor(name="Масса")
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
    fermentators = db.session.query(MascarponeSourdough).all()
    fermentator_small = [x for x in fermentators if x.name == "Small"][0]

    columns = [
        "Название SKU",
        "Процент",
        "Вкусовая добавка",
        "Имя бренда",
        "Вес нетто",
        "Срок хранения",
        "Коробки",
        "Скорость упаковки",
        "Линия",
        "Название форм фактора",
        "Выход",
    ]

    sku_data = df[columns]
    sku_data = sku_data.drop_duplicates().fillna("")
    for column_name in ["Выход"]:
        sku_data[column_name] = sku_data[column_name].apply(lambda x: json.loads(x))
    sku_data = sku_data.to_dict("records")
    for sku in sku_data:
        add_sku = MascarponeSKU(
            name=sku["Название SKU"],
            brand_name=sku["Имя бренда"],
            weight_netto=sku["Вес нетто"],
            shelf_life=sku["Срок хранения"],
            packing_speed=sku["Скорость упаковки"],
            in_box=sku["Коробки"],
        )

        line_name = LineName.MASCARPONE
        add_sku.line = [x for x in lines if x.name == line_name][0]
        add_sku.made_from_boilings = [
            x
            for x in boilings
            if (x.percent == sku["Процент"])
            & (x.flavoring_agent == sku["Вкусовая добавка"])
            & (x.line_id == add_sku.line.id)
        ]
        add_sku.group = [x for x in groups if x.name == sku["Название форм фактора"]][0]
        add_sku.form_factor = [x for x in form_factors if x.name == "Масса"][0]
        db.session.add(add_sku)
    db.session.commit()
