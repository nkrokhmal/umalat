from collections import defaultdict

import openpyxl
import pandas as pd

from utils_ak.builtin.collection import delistify
from utils_ak.openpyxl import cast_workbook

from app.models.helpers import cast_model
from app.models.mascarpone import MascarponeSKU


class BoilingPlanReaderException(Exception):
    ...


class BoilingPlanReader:
    def __init__(self, wb: openpyxl.Workbook, first_batches: dict | None = None) -> None:
        self.wb = cast_workbook(wb)
        self.first_batches: defaultdict = defaultdict(lambda: 1, first_batches)

    @property
    def _column_map(self) -> dict[str, str]:
        return {
            "Номер группы варок": "group_id",
            "Выход с одной варки, кг": "output",
            "SKU": "sku",
            "КГ Использовано": "kg",
        }

    def _read_workbook(self) -> pd.DataFrame:
        ws = self.wb["План варок"]
        values: list[list[str | float | int]] = []
        columns = [ws.cell(1, i).value for i in range(1, 10) if ws.cell(1, i).value]

        for i in range(2, 200):
            if not ws.cell(i, 2).value:
                continue

            values.append([ws.cell(i, j).value for j in range(1, len(columns) + 1)])

        df: pd.DataFrame = pd.DataFrame(values, columns=columns)
        df = df[self._column_map.keys()]
        df.rename(self._column_map, axis=1, inplace=True)
        return df.reset_index(drop=True)

    def _saturate(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[df["sku"] != "-"]
        df["group_id"] = df["group_id"].astype(int)
        df["batch_id"] = 0
        df["sku"] = df["sku"].apply(lambda sku: cast_model([MascarponeSKU], sku))

        df[["boiling", "sku_name", "group"]] = df["sku"].apply(
            lambda x: pd.Series([delistify(x.made_from_boilings, single=True), x.name, self._get_type(x)])
        )
        df[["boiling_id", "output_coeff"]] = df["boiling"].apply(
            lambda boiling: pd.Series([boiling.id, boiling.output_coeff])
        )
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
            volume, group, output_coeff = grp.iloc[0][["output", "group", "output_coeff"]]
            if abs(volume - output_coeff * grp["kg"].sum()) > 1:
                raise BoilingPlanReaderException("Указано неверное число килограмм в варке")

            df.loc[grp.index, "batch_id"] = self.first_batches[group]
            self.first_batches[group] += 1

        return df

    def parse(self) -> pd.DataFrame:
        df = self._read_workbook()
        df = self._saturate(df)
        df = self._set_batches(df)
        return df


__all__ = ["BoilingPlanReader", "BoilingPlanReaderException"]
