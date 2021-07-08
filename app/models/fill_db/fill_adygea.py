from ...enum import LineName
import pandas as pd
import json
from app.models import *


def read_params(fn="app/data/static/params/adygea.xlsx"):
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
        "Набор",
        "Коагуляция",
        "Слив",
        "Процент",
        "Вес нетто",
    ]
    bt_data = df[boiling_technologies_columns]
    bt_data = bt_data.drop_duplicates()
    bt_data = bt_data.to_dict("records")
    for bt in bt_data:
        line_name = LineName.ADYGEA
        technology = AdygeaBoilingTechnology(
            name=AdygeaBoilingTechnology.create_name(
                line=line_name,
                percent=bt["Процент"],
                weight=bt["Вес нетто"],
                form_factor=bt["Название форм фактора"],
            ),
            collecting_time=bt["Набор"],
            coagulation_time=bt["Коагуляция"],
            pouring_off_time=bt["Слив"],
        )

        db.session.add(technology)
        db.session.commit()


def fill_boilings():
    df = read_params()
    lines = db.session.query(Line).all()
    bts = db.session.query(AdygeaBoilingTechnology).all()
    columns = [
        "Название форм фактора",
        "Набор",
        "Коагуляция",
        "Слив",
        "Процент",
        "Вес нетто",
        "Вход",
        "Выход",
    ]
    b_data = df[columns]
    b_data = b_data.drop_duplicates()
    b_data = b_data.to_dict("records")
    for b in b_data:
        line_name = LineName.ADYGEA

        line_id = [x for x in lines if x.name == line_name][0].id
        bts_name = [
            x
            for x in bts
            if (x.collecting_time == b["Набор"])
            & (x.coagulation_time == b["Коагуляция"])
            & (x.pouring_off_time == b["Слив"])
            & (
                x.name
                == AdygeaBoilingTechnology.create_name(
                   line=line_name,
                   percent=b["Процент"],
                   weight=b["Вес нетто"],
                   form_factor=b["Название форм фактора"],
                )
            )
        ]
        boiling = AdygeaBoiling(
            percent=b["Процент"],
            boiling_technologies=bts_name,
            line_id=line_id,
            weight_netto=b["Вес нетто"],
            output_kg=b["Выход"],
            input_kg=b["Вход"]
        )
        db.session.add(boiling)
        db.session.commit()


def fill_form_factors():
    mass_ff = AdygeaFormFactor(name="Масса")
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
    boilings = db.session.query(AdygeaBoiling).all()
    form_factors = db.session.query(AdygeaFormFactor).all()
    groups = db.session.query(Group).all()

    columns = [
        "Название SKU",
        "Процент",
        "Название форм фактора",
        "Линия",
        "Имя бренда",
        "Вес нетто",
        "Коробки",
        "Kод",
    ]

    sku_data = df[columns]
    sku_data = sku_data.drop_duplicates()
    sku_data = sku_data.to_dict("records")
    for sku in sku_data:
        add_sku = AdygeaSKU(
            name=sku["Название SKU"],
            brand_name=sku["Имя бренда"],
            weight_netto=sku["Вес нетто"],
            code=sku["Kод"],
            in_box=sku["Коробки"],
        )

        line_name = LineName.ADYGEA
        add_sku.line = [x for x in lines if x.name == line_name][0]

        add_sku.made_from_boilings = [
            x
            for x in boilings
            if (x.percent == sku["Процент"]) &
               (x.line_id == add_sku.line.id) &
               (x.weight_netto == sku["Вес нетто"])
        ]
        add_sku.group = [x for x in groups if x.name == sku["Название форм фактора"]][0]
        add_sku.form_factor = [x for x in form_factors if x.name == "Масса"][0]
        db.session.add(add_sku)
    db.session.commit()
