from ...enum import LineName
import pandas as pd
import json
from app.models import *


def read_params(fn="app/data/params/ricotta.xlsx"):
    df = pd.read_excel(fn, index_col=0)
    return df


def fill_db():
    fill_boiling_technologies()
    fill_analysis_technology()
    fill_boilings()
    fill_form_factors()
    fill_sku()


def fill_boiling_technologies():
    df = read_params()
    boiling_technologies_columns = [
        "Нагрев",
        "Выдержка",
        "Сбор белка",
        "Заборс",
        "Слив",
        "Процент",
        "Вкусовая добавка",
    ]
    bt_data = df[boiling_technologies_columns]
    bt_data["Вкусовая добавка"] = bt_data["Вкусовая добавка"].fillna("")
    bt_data = bt_data.drop_duplicates()
    bt_data = bt_data.to_dict("records")
    for bt in bt_data:
        line_name = LineName.RICOTTA
        technology = RicottaBoilingTechnology(
            name=RicottaBoilingTechnology.create_name(
                line=line_name,
                percent=bt["Процент"],
                flavoring_agent=bt["Вкусовая добавка"],
            ),
            heating_time=bt["Нагрев"],
            delay_time=bt["Выдержка"],
            protein_harvest_time=bt["Сбор белка"],
            abandon_time=bt["Заборс"],
            pumping_out_time=bt["Слив"],
        )

        db.session.add(technology)
        db.session.commit()


def fill_analysis_technology():
    df = read_params()
    data = df[["Подготовка полуфабриката", "Анализ", "Перекачка"]]
    data = data.drop_duplicates()
    data = data.to_dict("records")
    for value in data:
        if any([not np.isnan(x) for x in value.values()]):
            technology = RicottaAnalysisTechnology(
                preparation_time=value["Подготовка полуфабриката"],
                analysis_time=value["Анализ"],
                pumping_time=value["Перекачка"],
            )
            db.session.add(technology)
    db.session.commit()


def fill_boilings():
    df = read_params()
    lines = db.session.query(Line).all()
    bts = db.session.query(RicottaBoilingTechnology).all()
    columns = [
        "Вкусовая добавка",
        "Процент",
        "Линия",
        "Нагрев",
        "Выдержка",
        "Сбор белка",
        "Заборс",
        "Слив",
    ]
    b_data = df[columns]
    b_data["Вкусовая добавка"] = b_data["Вкусовая добавка"].fillna("")
    b_data = b_data.drop_duplicates()
    b_data = b_data.to_dict("records")
    for b in b_data:
        line_name = LineName.RICOTTA
        line_id = [x for x in lines if x.name == LineName.RICOTTA][0].id
        bt_id = [
            x
            for x in bts
            if (x.heating_time == b["Нагрев"])
            & (x.delay_time == b["Выдержка"])
            & (x.protein_harvest_time == b["Сбор белка"])
            & (x.abandon_time == b["Заборс"])
            & (x.pumping_out_time == b["Слив"])
            & (
                x.name
                == RicottaBoilingTechnology.create_name(
                    line=line_name,
                    percent=b["Процент"],
                    flavoring_agent=b["Вкусовая добавка"],
                )
            )
        ][0].id
        boiling = RicottaBoiling(
            percent=b["Процент"],
            flavoring_agent=b["Вкусовая добавка"],
            boiling_technology_id=bt_id,
            line_id=line_id,
        )
        db.session.add(boiling)
        db.session.commit()


def fill_form_factors():
    mass_ff = RicottaFormFactor(name="Масса")
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
    lines = db.session.query(RicottaLine).all()
    boilings = db.session.query(RicottaBoiling).all()
    form_factors = db.session.query(RicottaFormFactor).all()
    groups = db.session.query(Group).all()

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
        "Вес форм фактора",
        "Название форм фактора",
    ]

    sku_data = df[columns]
    sku_data["Вкусовая добавка"] = sku_data["Вкусовая добавка"].fillna("")
    sku_data = sku_data.drop_duplicates()
    sku_data = sku_data.to_dict("records")
    for sku in sku_data:
        add_sku = RicottaSKU(
            name=sku["Название SKU"],
            brand_name=sku["Имя бренда"],
            weight_netto=sku["Вес нетто"],
            shelf_life=sku["Срок хранения"],
            packing_speed=sku["Скорость упаковки"],
            in_box=sku["Коробки"],
        )

        line_name = LineName.RICOTTA
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
