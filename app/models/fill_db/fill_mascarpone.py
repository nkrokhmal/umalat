import itertools
import os
import typing as tp

from dataclasses import dataclass

import pandas as pd

from app.enum import DepartmentName, LineName
from app.globals import db
from app.models.basic import Department, Group, Line, Washer
from app.models.mascarpone import (
    MascarponeBoiling,
    MascarponeBoilingTechnology,
    MascarponeFormFactor,
    MascarponeLine,
    MascarponeSKU,
)


@dataclass
class WasherData:
    original_name: str
    name: str
    time: int


class MascarponeFillingDBException(Exception):
    ...


def fill_db() -> None:
    suffix: str = "_test" if os.environ["DB_TYPE"] == "test" else ""
    df = pd.read_excel(f"app/data/static/params/mascarpone{suffix}.xlsx", index_col=0)

    is_valid, msg = validate_params(df)
    if not is_valid:
        raise MascarponeFillingDBException(msg)

    for obj in itertools.chain(
        fill_lines(),
        fill_washer(),
        fill_boiling_technologies(df),
        fill_boilings(df),
        fill_form_factors(),
        fill_sku(df),
    ):
        db.session.add(obj)
    db.session.commit()


def fill_washer() -> tp.Generator[Washer, None, None]:
    mascarpone_department = db.session.query(Department).filter_by(name=DepartmentName.MASCARPONE).first()

    for data in [
        WasherData("Мойка пастеризатора", "pasteurizer", 19 * 5),
        WasherData("Мойка сепаратора", "separator", 13 * 5),
        WasherData("Мойка 1-го и 2-го бака лишатричи+гомогенизатора", "homogenizer", 13 * 5),
        WasherData("Мойка буферного танка и фасовочника", "packer", 13 * 5),
        WasherData("Мойка бака №1", "tank_1", 13 * 5),
        WasherData("Мойка бака №2", "tank_2", 13 * 5),
        WasherData("Мойка теплообменника", "heat_exchanger", 13 * 5),
    ]:
        yield Washer(
            name=data.name,
            original_name=data.original_name,
            time=data.time,
            department_id=mascarpone_department.id,
        )


def validate_params(df: pd.DataFrame) -> tuple[bool, str | None]:
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
        "Константа",
        "Коэффициент",
    ]
    df = df[boiling_technologies_columns]
    df["Наличие лактозы"] = df["Наличие лактозы"].apply(lambda x: True if x.lower() == "да" else False)
    df.drop_duplicates(inplace=True)
    df.fillna("", inplace=True)

    bt_names: list[tuple[str, int]] = []

    for index, row in df.iterrows():
        bt_name = MascarponeBoilingTechnology.create_name(
            line=LineName.MASCARPONE,
            weight=row["Вес технология"],
            percent=row["Процент"],
            cheese_type=row["Название форм фактора"],
            flavoring_agent=row["Вкусовая добавка"],
            is_lactose=row["Наличие лактозы"],
        )

        same_technologies = [x for x in bt_names if x[0] == bt_name]
        if same_technologies:
            return (
                False,
                f"Технология {bt_name} имеет разные параметры. Проверьте строки {index} и {same_technologies[0][1]}",
            )

        bt_names.append((bt_name, index))
    return True, None


def fill_boiling_technologies(df: pd.DataFrame) -> tp.Generator[MascarponeBoilingTechnology, None, None]:
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

    for index, row in df.iterrows():
        bt_name = MascarponeBoilingTechnology.create_name(
            line=LineName.MASCARPONE,
            weight=row["Вес технология"],
            percent=row["Процент"],
            cheese_type=row["Название форм фактора"],
            flavoring_agent=row["Вкусовая добавка"],
            is_lactose=row["Наличие лактозы"],
        )
        yield MascarponeBoilingTechnology(
            name=bt_name,
            separation_time=row["Сепарация"],
            analysis_time=row["Анализ"],
            pouring_time=row["Налив"],
            heating_time=row["Нагрев"],
            pumping_time=row["Перекачка"],
            salting_time=row["Посолка"],
            ingredient_time=row["Ингридиенты"],
            weight=row["Вес технология"],
        )


def fill_boilings(df: pd.DataFrame) -> tp.Generator[MascarponeBoiling, None, None]:
    lines: list[Line] = db.session.query(Line).all()
    bts: list[MascarponeBoilingTechnology] = db.session.query(MascarponeBoilingTechnology).all()
    columns: list[str] = [
        "Вкусовая добавка",
        "Процент",
        "Наличие лактозы",
        "Название форм фактора",
        "Вес технология",
        "Коэффициент",
        "Константа",
        "Вход",
    ]
    df = df[columns]
    df["Наличие лактозы"] = df["Наличие лактозы"].apply(lambda x: True if x.lower() == "да" else False)
    df.drop_duplicates(inplace=True)
    df.fillna("", inplace=True)

    for item in df.to_dict("records"):
        line_name = "Маскарпоне" if item["Название форм фактора"] == "Маскарпоне" else "Кремчиз"
        line: int = next((x for x in lines if x.name == line_name))

        bts_name = MascarponeBoilingTechnology.create_name(
            line=LineName.MASCARPONE,
            weight=item["Вес технология"],
            percent=item["Процент"],
            cheese_type=item["Название форм фактора"],
            flavoring_agent=item["Вкусовая добавка"],
            is_lactose=item["Наличие лактозы"],
        )
        yield MascarponeBoiling(
            percent=item["Процент"],
            weight_netto=item["Вес технология"],
            flavoring_agent=item["Вкусовая добавка"],
            boiling_type=item["Название форм фактора"],
            is_lactose=item["Наличие лактозы"],
            boiling_technologies=[next((x for x in bts if x.name == bts_name), None)],
            output_coeff=item["Коэффициент"],
            output_constant=item["Константа"],
            line=line,
            input_kg=item["Вход"],
        )


def fill_form_factors() -> tp.Generator[MascarponeFormFactor, None, None]:
    yield MascarponeFormFactor(name="Масса")


def fill_sku(df: pd.DataFrame) -> tp.Generator[MascarponeSKU, None, None]:
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

        line_name = "Маскарпоне" if sku["Название форм фактора"] == "Маскарпоне" else "Кремчиз"
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
        yield add_sku


def fill_lines() -> tp.Generator[MascarponeLine, None, None]:
    for name, input_kg in (("Маскарпоне", 8000), ("Кремчиз", 8000)):
        yield MascarponeLine(name=name, department=Department.query.filter_by(name=DepartmentName.MASCARPONE).first())
