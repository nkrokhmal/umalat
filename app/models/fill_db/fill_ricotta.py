import typing as tp

import pandas as pd

from app.enum import DepartmentName, LineName
from app.globals import db
from app.models.basic import Department, Group, Line, Washer
from app.models.fill_db.base import BaseFiller, WasherData
from app.models.ricotta import RicottaBoiling, RicottaBoilingTechnology, RicottaFormFactor, RicottaLine, RicottaSKU


class RicottaFillerException(Exception):
    ...


TECHNOLOGIES_COLUMNS: list[str] = [
    "Набор сыворотки",
    "Нагрев",
    "молочная кислота/выдерживание",
    "слив сыворотки",
    "слив рикотты",
    "посолка/анализ",
    "Перекачивание",
]


class RicottaFiller(BaseFiller):
    def __init__(self) -> None:
        super().__init__(department="ricotta")

    def validate_params(self, df: pd.DataFrame) -> str | None:
        _df = self._filter_df(df, TECHNOLOGIES_COLUMNS + ["Процент", "Вкусовая добавка"])

        s: pd.Series = _df[["Процент", "Вкусовая добавка"]].apply(
            lambda row: RicottaBoilingTechnology.create_name(
                line=LineName.RICOTTA,
                percent=row["Процент"],
                flavoring_agent=row["Вкусовая добавка"],
            ),
            axis=1,
        )

        idx = self._not_unique_index(s)
        if idx is not None:
            return f"Технологии варки с одинаковы именем имеют разные параметры. Проверьте строки {idx[0]} и {idx[1]}"
        return

    def fill_form_factors(self, _: pd.DataFrame) -> tp.Generator[RicottaFormFactor, None, None]:
        yield RicottaFormFactor(name="Масса")

    def fill_lines(self, _: pd.DataFrame) -> tp.Generator[Line, None, None]:
        yield RicottaLine(
            name="Рикотта", input_kg=6500, department=Department.query.filter_by(name=DepartmentName.RICOTTA).first()
        )

    def fill_washers(self, df: pd.DataFrame) -> tp.Generator[Washer, None, None]:
        ricotta_department = db.session.query(Department).filter_by(name=DepartmentName.RICOTTA).first()
        for data in [
            WasherData("Мойка флокулятора №1", "flocculator_1", 12 * 5),
            WasherData("Мойка флокулятора №2", "flocculator_2", 12 * 5),
            WasherData("Мойка флокулятора №3", "flocculator_3", 12 * 5),
            WasherData("Мойка дренатора", "drain", 12 * 5),
            WasherData("Мойка 1-го и 2-го бакол лишатричи + Бертоли", "tanks", 12 * 5),
            WasherData("Мойка буферного танка и Фасовочника Грюнвальд", "buffer_tank", 12 * 5),
        ]:
            yield Washer(
                name=data.name,
                original_name=data.original_name,
                time=data.time,
                department_id=ricotta_department.id,
            )

    @staticmethod
    def _boiling_technology_name(row: dict | pd.Series) -> str:
        return RicottaBoilingTechnology.create_name(
            line=LineName.RICOTTA,
            percent=row["Процент"],
            flavoring_agent=row["Вкусовая добавка"],
        )

    def fill_boiling_technologies(self, df: pd.DataFrame) -> tp.Generator[RicottaBoilingTechnology, None, None]:
        _df = self._filter_df(df, TECHNOLOGIES_COLUMNS + ["Процент", "Вкусовая добавка"])

        for _, row in _df.iterrows():
            yield RicottaBoilingTechnology(
                name=self._boiling_technology_name(row),
                pouring_time=row["Набор сыворотки"],
                heating_time=row["Нагрев"],
                lactic_acid_time=row["молочная кислота/выдерживание"],
                drain_whey_time=row["слив сыворотки"],
                dray_ricotta_time=row["слив рикотты"],
                salting_time=row["посолка/анализ"],
                pumping_time=row["Перекачивание"],
            )

    def fill_boiling(self, df: pd.DataFrame) -> tp.Generator[RicottaBoiling, None, None]:
        technologies = db.session.query(RicottaBoilingTechnology).all()
        line = db.session.query(Line).filter_by(name=LineName.RICOTTA).first()

        _df = self._filter_df(df, ["Вкусовая добавка", "Процент", "Вход", "Выход"])

        for _, row in _df.iterrows():
            technology = next(t for t in technologies if t.name == self._boiling_technology_name(row))

            yield RicottaBoiling(
                percent=row["Процент"],
                flavoring_agent=row["Вкусовая добавка"],
                boiling_technologies=[technology],
                input_kg=row["Вход"],
                output_kg=row["Выход"],
                line=line,
            )

    def fill_sku(self, df: pd.DataFrame) -> tp.Generator[RicottaSKU, None, None]:
        columns: list[str] = [
            "Название SKU",
            "Процент",
            "Вкусовая добавка",
            "Имя бренда",
            "Вес нетто",
            "Коробки",
            "Скорость упаковки",
            "Линия",
            "Вес форм фактора",
            "Название форм фактора",
            "Выход",
            "Kод",
        ]

        line = db.session.query(Line).filter_by(name=LineName.RICOTTA).first()
        boilings = db.session.query(RicottaBoiling).all()
        form_factors = db.session.query(RicottaFormFactor).all()
        groups = db.session.query(Group).all()

        _df = self._filter_df(df, columns)

        for _, row in _df.iterrows():
            sku = RicottaSKU(
                name=row["Название SKU"],
                brand_name=row["Имя бренда"],
                weight_netto=row["Вес нетто"],
                packing_speed=row["Скорость упаковки"],
                in_box=row["Коробки"],
                code=row["Kод"],
                line=line,
            )

            sku.made_from_boilings = [
                x for x in boilings if x.percent == row["Процент"] and x.flavoring_agent == row["Вкусовая добавка"]
            ]
            sku.group = next(x for x in groups if x.name == row["Название форм фактора"])
            sku.form_factor = next(x for x in form_factors if x.name == "Масса")
            yield sku


__all__ = [
    "RicottaFiller",
]
