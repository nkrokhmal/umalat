import itertools
import os
import typing as tp

from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd

from app.globals import db
from app.models import SKU, Boiling, BoilingTechnology, FormFactor, Line, Washer


@dataclass
class WasherData:
    original_name: str
    name: str
    time: int


@dataclass
class ValidateData:
    columns: list[str]
    group_columns: list[str]
    msg: str


class ParametersException(Exception):
    ...


class BaseFiller(ABC):
    def __init__(self, department: tp.Literal["mascarpone", "ricotta", "brynza"]) -> None:
        self.department = department

    def _read_df(self) -> pd.DataFrame:
        suffix: str = "_test" if os.environ["DB_TYPE"] == "test" else ""
        return pd.read_excel(f"app/data/static/params/{self.department}{suffix}.xlsx", index_col=0)

    @staticmethod
    def _filter_df(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        _df = df[columns]
        _df.drop_duplicates(inplace=True)
        _df.fillna("", inplace=True)
        return _df

    @staticmethod
    def _not_unique_index(values: pd.Series) -> tuple[int, ...] | None:
        duplicates = values[values.duplicated(keep=False)]
        pairs: pd.Series = duplicates.groupby(duplicates).apply(list).tolist()
        if not pairs:
            return None

        return values[values == pairs[0][0]].index.tolist()

    @abstractmethod
    def validate_params(self, df: pd.DataFrame) -> str | None:
        ...

    @abstractmethod
    def fill_lines(self, df: pd.DataFrame) -> tp.Generator[Line, None, None]:
        ...

    @abstractmethod
    def fill_washers(self, df: pd.DataFrame) -> tp.Generator[Washer, None, None]:
        ...

    @abstractmethod
    def fill_form_factors(self, df: pd.DataFrame) -> tp.Generator[FormFactor, None, None]:
        ...

    @abstractmethod
    def fill_boiling_technologies(self, df: pd.DataFrame) -> tp.Generator[BoilingTechnology, None, None]:
        ...

    @abstractmethod
    def fill_boiling(self, df: pd.DataFrame) -> tp.Generator[Boiling, None, None]:
        ...

    @abstractmethod
    def fill_sku(self, df: pd.DataFrame) -> tp.Generator[SKU, None, None]:
        ...

    def fill_db(self) -> None:
        df = self._read_df()
        msg = self.validate_params(df)
        if msg is not None:
            raise ParametersException(msg)

        for generator in [
            self.fill_lines(df),
            self.fill_washers(df),
            self.fill_form_factors(df),
            self.fill_boiling_technologies(df),
            self.fill_boiling(df),
            self.fill_sku(df),
        ]:
            for item in generator:
                db.session.add(item)

        db.session.commit()


__all__ = [
    "BaseFiller",
    "WasherData",
]
