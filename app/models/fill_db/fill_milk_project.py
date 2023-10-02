import os

import pandas as pd

from app.enum import LineName
from app.globals import db
from app.models.basic import Group, Line
from app.models.milk_project import (
    MilkProjectBoiling,
    MilkProjectBoilingTechnology,
    MilkProjectFormFactor,
    MilkProjectSKU,
)


def read_params():
    if os.environ["DB_TYPE"] == "test":
        fn = "app/data/static/params/milk_project_test.xlsx"
    else:
        fn = "app/data/static/params/milk_project.xlsx"
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
        "Смесь",
        "Производство",
        "Красный",
        "Процент",
        "Вес нетто",
    ]
    bt_data = df[boiling_technologies_columns]
    bt_data = bt_data.drop_duplicates()
    bt_data = bt_data.to_dict("records")
    for bt in bt_data:
        line_name = LineName.MILK_PROJECT
        technology = MilkProjectBoilingTechnology(
            name=MilkProjectBoilingTechnology.create_name(
                line=line_name,
                percent=bt["Процент"],
                weight=bt["Вес нетто"],
                form_factor=bt["Название форм фактора"],
            ),
            mixture_collecting_time=bt["Смесь"],
            processing_time=bt["Производство"],
            red_time=bt["Красный"],
        )

        db.session.add(technology)
        db.session.commit()


def fill_boilings():
    df = read_params()
    lines = db.session.query(Line).all()
    bts = db.session.query(MilkProjectBoilingTechnology).all()
    columns = [
        "Название форм фактора",
        "Смесь",
        "Производство",
        "Красный",
        "Процент",
        "Вес нетто",
        "Выход",
        "Название варки",
    ]
    b_data = df[columns]
    b_data = b_data.drop_duplicates()
    b_data = b_data.to_dict("records")
    for b in b_data:
        line_name = LineName.MILK_PROJECT

        line_id = [x for x in lines if x.name == line_name][0].id
        bts_name = [
            x
            for x in bts
            if (x.mixture_collecting_time == b["Смесь"])
            & (x.processing_time == b["Производство"])
            & (x.red_time == b["Красный"])
            & (
                x.name
                == MilkProjectBoilingTechnology.create_name(
                    line=line_name,
                    percent=b["Процент"],
                    weight=b["Вес нетто"],
                    form_factor=b["Название форм фактора"],
                )
            )
        ]
        boiling = MilkProjectBoiling(
            percent=b["Процент"],
            name=b["Название варки"],
            boiling_technologies=bts_name,
            line_id=line_id,
            weight_netto=b["Вес нетто"],
            output_kg=b["Выход"],
            # todo: delete
            equipment_check_time=10,
        )
        db.session.add(boiling)
        db.session.commit()


def fill_form_factors():
    mass_ff = MilkProjectFormFactor(name="Масса")
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
    boilings = db.session.query(MilkProjectBoiling).all()
    form_factors = db.session.query(MilkProjectFormFactor).all()
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
        "Название варки",
    ]

    sku_data = df[columns]
    sku_data = sku_data.drop_duplicates()
    sku_data = sku_data.to_dict("records")
    for sku in sku_data:
        add_sku = MilkProjectSKU(
            name=sku["Название SKU"],
            brand_name=sku["Имя бренда"],
            weight_netto=sku["Вес нетто"],
            code=sku["Kод"],
            in_box=sku["Коробки"],
        )

        line_name = LineName.MILK_PROJECT
        add_sku.line = [x for x in lines if x.name == line_name][0]

        add_sku.made_from_boilings = [
            x
            for x in boilings
            if (x.percent == sku["Процент"])
            & (x.line_id == add_sku.line.id)
            & (x.weight_netto == sku["Вес нетто"])
            & (x.name == sku["Название варки"])
        ]
        add_sku.group = [x for x in groups if x.name == sku["Название форм фактора"]][0]
        add_sku.form_factor = [x for x in form_factors if x.name == "Масса"][0]
        db.session.add(add_sku)
    db.session.commit()
