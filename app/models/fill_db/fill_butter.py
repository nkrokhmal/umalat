import pandas as pd
import json
from app.models import *


def read_params():
    if os.environ["DB_TYPE"] == "test":
        fn = "app/data/static/params/butter_test.xlsx"
    else:
        fn = "app/data/static/params/butter.xlsx"
    df = pd.read_excel(fn, index_col=0)
    return df


def fill_db():
    fill_boiling_technologies()
    fill_boilings()
    fill_form_factors()
    fill_sku()


def fill_boiling_technologies():
    df = read_params()
    boiling_technologies_columns = [
        "Название форм фактора",
        "Разгон сепаратора",
        "Пастеризация",
        "Набор",
        "Процент",
        "Наличие лактозы",
        "Вкусовая добавка",
        "Вес нетто",
    ]
    bt_data = df[boiling_technologies_columns]
    bt_data["Вкусовая добавка"] = bt_data["Вкусовая добавка"].fillna("")
    bt_data = bt_data.drop_duplicates()
    bt_data = bt_data.to_dict("records")
    for bt in bt_data:
        line_name = LineName.BUTTER
        technology = ButterBoilingTechnology(
            name=ButterBoilingTechnology.create_name(
                line=line_name, percent=bt["Процент"],
                weight=bt["Вес нетто"],
                form_factor=bt["Название форм фактора"],
                flavoring_agent=bt["Вкусовая добавка"],
                is_lactose=True if bt["Наличие лактозы"] == "Да" else False
            ),
            separator_runaway_time=bt["Разгон сепаратора"],
            pasteurization_time=bt["Пастеризация"],
            increasing_temperature_time=bt["Набор"],
        )

        db.session.add(technology)
        db.session.commit()


def fill_boilings():
    df = read_params()
    lines = db.session.query(Line).all()
    bts = db.session.query(ButterBoilingTechnology).all()
    columns = [
        "Название форм фактора",
        "Разгон сепаратора",
        "Пастеризация",
        "Набор",
        "Процент",
        "Наличие лактозы",
        "Вкусовая добавка",
        "Вес нетто",
    ]
    b_data = df[columns]
    b_data["Вкусовая добавка"] = b_data["Вкусовая добавка"].fillna("")
    b_data = b_data.drop_duplicates()
    b_data = b_data.to_dict("records")
    for b in b_data:
        line_name = LineName.BUTTER
        line_id = [x for x in lines if x.name == line_name][0].id
        bts_name = [
            x
            for x in bts
            if (x.separator_runaway_time == b["Разгон сепаратора"])
            & (x.pasteurization_time == b["Пастеризация"])
            & (x.increasing_temperature_time == b["Набор"])
            & (
                x.name
                == ButterBoilingTechnology.create_name(
                   line=line_name,
                   percent=b["Процент"],
                   weight=b["Вес нетто"],
                   form_factor=b["Название форм фактора"],
                   flavoring_agent=b["Вкусовая добавка"],
                   is_lactose=True if b["Наличие лактозы"] == "Да" else False
                )
            )
        ]
        boiling = ButterBoiling(
            percent=b["Процент"],
            boiling_technologies=bts_name,
            line_id=line_id,
            weight_netto=b["Вес нетто"],
            flavoring_agent=b["Вкусовая добавка"],
            is_lactose=True if b["Наличие лактозы"] == "Да" else False,
        )
        db.session.add(boiling)
        db.session.commit()


def fill_form_factors():
    mass_ff = ButterFormFactor(name="Масса")
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
    boilings = db.session.query(ButterBoiling).all()
    form_factors = db.session.query(ButterFormFactor).all()
    groups = db.session.query(Group).all()

    columns = [
        "Название SKU",
        "Процент",
        "Наличие лактозы",
        "Вкусовая добавка",
        "Название форм фактора",
        "Линия",
        "Имя бренда",
        "Вес нетто",
        "Коробки",
        "Скорость упаковки",
        "Kод",
    ]

    sku_data = df[columns]
    sku_data["Вкусовая добавка"] = sku_data["Вкусовая добавка"].fillna("")
    sku_data = sku_data.drop_duplicates()
    sku_data = sku_data.to_dict("records")
    for sku in sku_data:
        add_sku = ButterSKU(
            name=sku["Название SKU"],
            brand_name=sku["Имя бренда"],
            weight_netto=sku["Вес нетто"],
            packing_speed=sku["Скорость упаковки"],
            code=sku["Kод"],
            in_box=sku["Коробки"],
        )

        line_name = LineName.BUTTER
        add_sku.line = [x for x in lines if x.name == line_name][0]

        add_sku.made_from_boilings = [
            x
            for x in boilings
            if (x.percent == sku["Процент"]) &
               (x.line_id == add_sku.line.id) &
               (x.flavoring_agent == sku["Вкусовая добавка"]) &
               (x.is_lactose == (True if sku["Наличие лактозы"] == "Да" else False)) &
               (x.weight_netto == sku["Вес нетто"])
        ]
        add_sku.group = [x for x in groups if x.name == sku["Название форм фактора"]][0]
        add_sku.form_factor = [x for x in form_factors if x.name == "Масса"][0]
        db.session.add(add_sku)
    db.session.commit()
