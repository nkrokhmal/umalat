from collections import defaultdict
from dataclasses import dataclass

import openpyxl
import pandas as pd

from utils_ak.openpyxl import cast_workbook

from app.globals import db
from app.models.helpers import cast_model
from app.models.mascarpone import MascarponeSKU
from app.utils.mascarpone.utils import MascarponeBoilingsHandler


class BoilingPlanReaderException(Exception):
    ...


@dataclass
class HugeBoiling:
    skus: list[dict] | None = None
    input_kg: int = 0
    output_kg: int = 0
    type: str | None = None

    def __post_init__(self) -> None:
        self.skus = []


COLUMNS: dict[str, str] = {
    "Номер группы варок": "group_id",
    "Линия": "line",
    "Тип варки": "boiling_type",
    "SKU": "sku_name",
    "Кг": "kg",
    "Остатки": "leftovers",
    "Выход, кг": "output_kg",
    "Вход, кг": "input_kg",
}


class BoilingPlanReader:
    def __init__(self, wb: openpyxl.Workbook, first_batches: dict | None = None) -> None:
        self.wb = cast_workbook(wb)
        self.first_batches: defaultdict = defaultdict(lambda: 1, first_batches)

    def _read_workbook(self) -> list[HugeBoiling]:
        ws = self.wb["План варок"]
        boilings: list[HugeBoiling] = []
        boiling = HugeBoiling()
        skus = db.session.query(MascarponeSKU).all()

        for i in range(2, 200):
            sku_name = ws.cell(i, 4).value
            match sku_name:
                case "-":
                    item = {column: ws.cell(i, j + 1).value for j, column in enumerate(COLUMNS.values())}
                    boiling.input_kg = item["input_kg"]
                    boiling.output_kg = item["output_kg"]
                    boilings.append(boiling)

                    boiling = HugeBoiling()
                case None | "":
                    continue
                case _:
                    item = {column: ws.cell(i, j + 1).value for j, column in enumerate(COLUMNS.values())}
                    sku = next((sku for sku in skus if sku.name == item["sku_name"]), None)
                    if sku is None:
                        raise BoilingPlanReaderException(f"Неверно указано имя sku {item['name']}, линия {i}")
                    boiling.type = self._get_type(sku)
                    boiling.skus.append(item)
        return boilings

    def _unwind_boilings(self, boilings: list[HugeBoiling]) -> pd.DataFrame:
        dfs = []
        group_id = 1
        for boiling in boilings:
            match boiling.type:
                case "cream":

                    if not 390 <= boiling.input_kg <= 810:
                        raise BoilingPlanReaderException(f"Указано неверное число килограмм в варке {boiling.type}")

                    df = pd.DataFrame(boiling.skus)
                    df[["output_kg", "input_kg", "group_id", "group"]] = (
                        boiling.output_kg,
                        boiling.input_kg,
                        group_id,
                        boiling.type,
                    )
                    dfs.append(df)
                    group_id += 1
                case _:
                    num: int = int(boiling.input_kg / 1000)
                    if boiling.input_kg / 1000 - num > 0.1:
                        raise BoilingPlanReaderException(f"Указано неверное число килограмм в варке {boiling.type}")

                    max_weight: float = boiling.output_kg / num
                    handler = MascarponeBoilingsHandler()
                    handler.handle_group(boiling.skus, max_weight=max_weight, weight_key="kg")
                    for group in handler.boilings:
                        df = pd.DataFrame(group.skus)
                        df[["output_kg", "input_kg", "group_id", "group"]] = (max_weight, 1000, group_id, boiling.type)
                        dfs.append(df)
                        group_id += 1
        return pd.concat(dfs)

    def _saturate(self, df: pd.DataFrame) -> pd.DataFrame:
        df.index = range(len(df))
        df["batch_id"] = 0

        df["sku"] = df["sku_name"].apply(lambda x: cast_model([MascarponeSKU], x))
        df["boiling"] = df["sku"].apply(lambda x: x.made_from_boilings[0])
        df["boiling_id"] = df["boiling"].apply(lambda boiling: boiling.id)
        df["semifinished_group"] = df["group"].apply(lambda group: group if group != "cottage_cheese" else "robiola")

        return df

    @staticmethod
    def _get_type(sku: MascarponeSKU) -> str:
        match sku.group.name.lower():
            case "сливки":
                return "cream"
            case "кремчиз":
                return "cream_cheese"
            case "робиола":
                return "robiola"
            case "творожный":
                return "cottage_cheese"
            case "маскарпоне":
                return "mascarpone"
            case _:
                raise BoilingPlanReaderException(
                    """
                    Неизвестный тип максарпоне. В названии должен присутствовать один из типов:
                    Сливки, Кремчиз, Робиола, Творожный, Маскарпоне
                    """
                )

    def _set_batches(self, df: pd.DataFrame) -> pd.DataFrame:
        for _, grp in df.groupby("group_id"):
            group = grp.iloc[0][["group"]]
            df.loc[grp.index, "batch_id"] = self.first_batches[group[0]]
            self.first_batches[group[0]] += 1

        return df

    def parse(self) -> pd.DataFrame:
        boilings = self._read_workbook()
        df = self._unwind_boilings(boilings)
        df = self._saturate(df)
        df = self._set_batches(df)
        return df


__all__ = ["BoilingPlanReader", "BoilingPlanReaderException"]
