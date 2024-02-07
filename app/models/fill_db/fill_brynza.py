import typing as tp

import pandas as pd

from app.enum import DepartmentName, LineName
from app.globals import db
from app.models.basic import Department, Group, Line, Washer
from app.models.brynza import BrynzaBoiling, BrynzaBoilingTechnology, BrynzaFormFactor, BrynzaLine, BrynzaSKU
from app.models.fill_db.base import BaseFiller, ValidateData, WasherData


class BrynzaFillerException(Exception):
    ...


TECHNOLOGIES_COLUMNS: list[str] = [
    "Скорость варки",
    "Налив",
    "Схватка",
    "Резка",
    "Слив",
    "Посолка",
]


class BrynzaFiller(BaseFiller):
    def __init__(self) -> None:
        super().__init__(department="brynza")

    def validate_params(self, df: pd.DataFrame) -> str | None:
        for data in [
            ValidateData(
                columns=TECHNOLOGIES_COLUMNS + ["Процент"],
                group_columns=["Процент"],
                msg="Технологии варки с одинаковым именем имеют разные параметры. Проверьте строки {} и {}",
            ),
        ]:
            _df = self._filter_df(df, data.columns)
            s: pd.Series = _df[data.group_columns].apply(tuple, axis=1)
            idx = self._not_unique_index(s)
            if idx is not None:
                return data.msg.format(idx[0], idx[1])

        return

    def fill_form_factors(self, _: pd.DataFrame) -> tp.Generator[BrynzaFormFactor, None, None]:
        yield BrynzaFormFactor(name="Масса")

    def fill_lines(self, _: pd.DataFrame) -> tp.Generator[Line, None, None]:
        yield BrynzaLine(name="Брынза", department=Department.query.filter_by(name=DepartmentName.ADYGEA).first())

    def fill_washers(self, df: pd.DataFrame) -> tp.Generator[Washer, None, None]:
        adygea_department = db.session.query(Department).filter_by(name=DepartmentName.ADYGEA).first()
        for data in [
            WasherData("Мойка брынзы", "brynza_washer", 25),
        ]:
            yield Washer(
                name=data.name,
                original_name=data.original_name,
                time=data.time,
                department_id=adygea_department.id,
            )

    @staticmethod
    def _boiling_technology_name(row: dict | pd.Series) -> str:
        return BrynzaBoilingTechnology.create_name(
            form_factor="Брынза",
            line=LineName.BRYNZA,
            percent=row["Процент"],
            weight=row["Вес нетто"],
        )

    def fill_boiling_technologies(self, df: pd.DataFrame) -> tp.Generator[BrynzaBoilingTechnology, None, None]:
        _df = self._filter_df(df, TECHNOLOGIES_COLUMNS + ["Процент", "Вес нетто"])

        for _, row in _df.iterrows():
            yield BrynzaBoilingTechnology(
                name=self._boiling_technology_name(row),
                boiling_speed=row["Скорость варки"],
                pouring_time=row["Налив"],
                soldification_time=row["Схватка"],
                cutting_time=row["Резка"],
                pouring_off_time=row["Слив"],
                salting_time=row["Посолка"],
            )

    def fill_boiling(self, df: pd.DataFrame) -> tp.Generator[BrynzaBoiling, None, None]:
        technologies = db.session.query(BrynzaBoilingTechnology).all()
        line = db.session.query(Line).filter_by(name=LineName.BRYNZA).first()

        _df = self._filter_df(df, ["Процент", "Вес нетто"])

        for _, row in _df.iterrows():
            name = self._boiling_technology_name(row)
            yield BrynzaBoiling(
                percent=row["Процент"],
                weight=row["Вес нетто"],
                boiling_technologies=[t for t in technologies if t.name == name],
                line=line,
            )

    def fill_sku(self, df: pd.DataFrame) -> tp.Generator[BrynzaSKU, None, None]:
        columns: list[str] = [
            "Название SKU",
            "Процент",
            "Имя бренда",
            "Вес нетто",
            "Коробки",
            "Линия",
            "Вес форм фактора",
            "Название форм фактора",
            "Скорость варки",
            "Kод",
        ]

        line = db.session.query(Line).filter_by(name=LineName.BRYNZA).first()
        boilings = db.session.query(BrynzaBoiling).all()
        form_factors = db.session.query(BrynzaFormFactor).all()
        groups = db.session.query(Group).all()

        _df = self._filter_df(df, columns)

        for _, row in _df.iterrows():
            yield BrynzaSKU(
                name=row["Название SKU"],
                brand_name=row["Имя бренда"],
                weight_netto=row["Вес нетто"],
                packing_speed=row["Скорость варки"],
                in_box=row["Коробки"],
                code=row["Kод"],
                line=line,
                made_from_boilings=[
                    b for b in boilings if b.percent == row["Процент"] and b.weight == row["Вес нетто"]
                ],
                group=next(x for x in groups if x.name == row["Название форм фактора"]),
                form_factor=next(x for x in form_factors if x.name == "Масса"),
            )


__all__ = [
    "BrynzaFiller",
]
