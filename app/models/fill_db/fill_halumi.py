import typing as tp

import pandas as pd

from app.enum import DepartmentName, LineName
from app.globals import db
from app.models.basic import Department, Line, Washer
from app.models.halumi import HalumiBoiling, HalumiBoilingTechnology, HalumiFormFactor, HalumiLine, HalumiSKU
from app.models.fill_db.base import BaseFiller


class HalumiFillerException(Exception):
    ...


class HalumiFiller(BaseFiller):
    def __init__(self) -> None:
        super().__init__(department="halumi")

    def validate_params(self, df: pd.DataFrame) -> str | None:
        return

    def fill_form_factors(self, _: pd.DataFrame) -> tp.Generator[HalumiFormFactor, None, None]:
        yield HalumiFormFactor(name="Масса")

    def fill_lines(self, _: pd.DataFrame) -> tp.Generator[Line, None, None]:
        yield HalumiLine(name="Халуми", department=Department.query.filter_by(name=DepartmentName.ADYGEA).first())

    def fill_washers(self, df: pd.DataFrame) -> tp.Generator[Washer, None, None]:
        return
        yield

    def fill_boiling_technologies(self, df: pd.DataFrame) -> tp.Generator[HalumiBoilingTechnology, None, None]:
        yield HalumiBoilingTechnology(
            name="Технология варки халуми",
            collecting_time=5,
            coagulation_time=25,
            pouring_off_time=10,
        )

    def fill_boiling(self, df: pd.DataFrame) -> tp.Generator[HalumiBoiling, None, None]:
        technology = db.session.query(HalumiBoilingTechnology).first()
        line = db.session.query(Line).filter_by(name=LineName.HALUMI).first()

        yield HalumiBoiling(
            weight_netto=0,
            percent=0,
            boiling_technologies=[technology],
            line=line,
        )

    def fill_sku(self, df: pd.DataFrame) -> tp.Generator[HalumiSKU, None, None]:
        return
        yield


__all__ = [
    "HalumiFiller",
]
