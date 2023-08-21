import os
import typing as tp

import numpy as np
import pandas as pd

from app.enum import LineName
from app.globals import db
from app.models.basic import Group, Line
from app.models.mascarpone import (
    MascarponeBoiling,
    MascarponeBoilingTechnology,
    MascarponeFormFactor,
    MascarponeLine,
    MascarponeSKU,
)


def read_params_df() -> pd.DataFrame:
    suffix: str = "_test" if os.environ["DB_TYPE"] == "test" else ""
    return pd.read_excel(f"app/data/static/params/mascarpone{suffix}.xlsx", index_col=0)


def fill_db() -> None:
    fill_boiling_technologies()
    fill_boilings()
    fill_form_factors()
    fill_sku()


def fill_boiling_technologies() -> None:
    """
    Adds boiling technologies into db from the excel params
    """
    df = read_params_df()
    boiling_technologies_columns = [
        "Название форм фактора",
        "Сепарация",
        "Анализ",
        "Налив",
        "Перекачка",
        "Нагрев",
        "Посолка",
        "Ингридиенты",
        "Процент",
        "Наличие лактозы",
        "Вкусовая добавка",
        "Вес технология",
    ]
    df = df[boiling_technologies_columns]
    df["Наличие лактозы"] = df["Наличие лактозы"].apply(lambda x: True if x.lower() == "да" else False)
    df.drop_duplicates(inplace=True)
    df.fillna("", inplace=True)

    for item in df.to_dict("records"):
        technology = MascarponeBoilingTechnology(
            name=MascarponeBoilingTechnology.create_name(
                line=LineName.MASCARPONE,
                weight=item["Вес технология"],
                percent=item["Процент"],
                cheese_type=item["Название форм фактора"],
                flavoring_agent=item["Вкусовая добавка"],
                is_lactose=item["Наличие лактозы"],
            ),
            separation_time=item["Сепарация"],
            analysis_time=item["Анализ"],
            pouring_time=item["Налив"],
            heating_time=item["Нагрев"],
            pumping_time=item["Перекачка"],
            salting_time=item["Посолка"],
            ingredient_time=item["Ингридиенты"],
            weight=item["Вес технология"],
        )
        db.session.add(technology)
    db.session.commit()


def fill_boilings() -> None:
    df: pd.DataFrame = read_params_df()
    lines: list[Line] = db.session.query(Line).all()
    bts: list[MascarponeBoilingTechnology] = db.session.query(MascarponeBoilingTechnology).all()
    columns: list[str] = [
        "Вкусовая добавка",
        "Процент",
        "Наличие лактозы",
        "Название форм фактора",
        "Вес технология",
        "Коэффициент",
        "Выход",
    ]
    df = df[columns]
    df["Наличие лактозы"] = df["Наличие лактозы"].apply(lambda x: True if x.lower() == "да" else False)
    df.drop_duplicates(inplace=True)
    df.fillna("", inplace=True)
    line_id: int = next((x.id for x in lines if x.name == LineName.MASCARPONE))

    for item in df.to_dict("records"):
        bts_name = MascarponeBoilingTechnology.create_name(
            line=LineName.MASCARPONE,
            weight=item["Вес технология"],
            percent=item["Процент"],
            cheese_type=item["Название форм фактора"],
            flavoring_agent=item["Вкусовая добавка"],
            is_lactose=item["Наличие лактозы"],
        )
        boiling = MascarponeBoiling(
            percent=item["Процент"],
            weight_netto=item["Вес технология"],
            flavoring_agent=item["Вкусовая добавка"],
            boiling_type=item["Название форм фактора"],
            is_lactose=item["Наличие лактозы"],
            boiling_technologies=[next((x for x in bts if x.name == bts_name), None)],
            output_coeff=item["Коэффициент"],
            line_id=line_id,
            output_kg=item["Выход"],
        )

        db.session.add(boiling)
    db.session.commit()


def fill_form_factors() -> None:
    mass_ff = MascarponeFormFactor(name="Масса")
    db.session.add(mass_ff)
    db.session.commit()


def _cast_non_nan(obj: tp.Any) -> tp.Any:
    if obj is None:
        return
    elif np.isnan(obj):
        return
    else:
        return obj


def fill_sku() -> None:
    df = read_params_df()
    lines = db.session.query(MascarponeLine).all()
    boilings = db.session.query(MascarponeBoiling).all()
    form_factors = db.session.query(MascarponeFormFactor).all()
    groups = db.session.query(Group).all()

    columns = [
        "Название SKU",
        "Название форм фактора",
        "Процент",
        "Вкусовая добавка",
        "Наличие лактозы",
        "Имя бренда",
        "Вес",
        "Вес технология",
        "Коробки",
        "Скорость фасовки",
        "Название форм фактора",
        "Kод",
    ]

    df = df[columns]
    df["Наличие лактозы"] = df["Наличие лактозы"].apply(lambda x: True if x.lower() == "да" else False)
    df.drop_duplicates(inplace=True)
    df.fillna("", inplace=True)

    for sku in df.to_dict("records"):
        add_sku = MascarponeSKU(
            name=sku["Название SKU"],
            brand_name=sku["Имя бренда"],
            weight_netto=sku["Вес"],
            shelf_life=0,
            packing_speed=sku["Скорость фасовки"],
            in_box=sku["Коробки"],
            code=sku["Kод"],
        )

        line_name = LineName.MASCARPONE
        add_sku.line = next((x for x in lines if x.name == line_name), None)
        add_sku.made_from_boilings = [
            x
            for x in boilings
            if (x.percent == sku["Процент"])
            & (x.flavoring_agent == sku["Вкусовая добавка"])
            & (x.is_lactose == sku["Наличие лактозы"])
            & (x.weight_netto == sku["Вес технология"])
            & (x.line_id == add_sku.line.id)
            & (x.boiling_type == sku["Название форм фактора"])
        ]

        add_sku.group = next((x for x in groups if x.name == sku["Название форм фактора"]), None)
        add_sku.form_factor = next((x for x in form_factors if x.name == "Масса"), None)
        db.session.add(add_sku)
    db.session.commit()
