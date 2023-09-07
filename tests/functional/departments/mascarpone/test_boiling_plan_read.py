from collections import defaultdict
from pathlib import Path

import openpyxl
import pandas as pd
import pytest

from pytest import fixture

from app.utils.mascarpone.boiling_plan_read import BoilingPlanReader, BoilingPlanReaderException


MASCARPONE_TEST_DIR: Path = Path("app/data/tests/mascarpone")


@fixture(scope="module")
def batches() -> dict[str, int]:
    return defaultdict(lambda: 1, dict(robiola=10, cottage_cheese=2, cream=4))


@fixture(scope="module")
def wb() -> openpyxl.Workbook:
    return openpyxl.load_workbook(
        filename=MASCARPONE_TEST_DIR / "boiling.xlsx",
        data_only=True,
    )


@fixture(scope="module")
def wb_corrupted() -> openpyxl.Workbook:
    return openpyxl.load_workbook(
        filename=MASCARPONE_TEST_DIR / "boiling_corrupted.xlsx",
        data_only=True,
    )


def test_boiling_plan_reader(wb: openpyxl.Workbook, batches: dict[str, int]) -> None:
    reader = BoilingPlanReader(wb=wb, first_batches=batches)
    df = reader.parse()
    ground_truth = pd.DataFrame(
        data=[
            [1, 'Сливки Panna da Montare "Unagrande", 35,1%, 0,5 кг, пл/с', batches["cream"], 300],
            [2, 'Сливки Panna Fresca "Unagrande", 38%, 0,5 л, пл/с', batches["cream"] + 1, 400],
            [3, 'Маскарпоне "Pretto", 80%, 0,5 кг, пл/с', batches["mascarpone"], 600.0],
            [4, 'Маскарпоне "Pretto", 80%, 0,5 кг, пл/с', batches["mascarpone"] + 1, 600.0],
            [5, 'Маскарпоне "Pretto", 80%, 0,5 кг, пл/с', batches["mascarpone"] + 2, 600.0],
            [6, 'Маскарпоне "Unagrande", 80%, 0,25 кг, пл/с', batches["mascarpone"] + 3, 600.0],
            [7, 'Маскарпоне "Unagrande", 80%, 0,25 кг, пл/с', batches["mascarpone"] + 4, 600.0],
            [8, 'Кремчиз "Фермерская коллекция", 70%, 0,2 кг, пл/с', batches["cream_cheese"], 370.0],
            [9, 'Кремчиз "Фермерская коллекция", 70%, 0,2 кг, пл/с', batches["cream_cheese"] + 1, 130.0],
            [9, 'Кремчиз "Pretto", 70%, 0,2 кг, пл/с', batches["cream_cheese"] + 1, 240.0],
            [10, 'Кремчиз "Pretto", 70%, 0,2 кг, пл/с', batches["cream_cheese"] + 2, 370.0],
            [11, "Творожный сливочный «LiebenDorf», 70%, 0,14 кг, п/с", batches["cottage_cheese"], 525.0],
            [12, "Творожный сливочный «LiebenDorf», 70%, 0,14 кг, п/с", batches["cottage_cheese"] + 1, 525.0],
        ],
        columns=["group_id", "sku_name", "batch_id", "kg"],
    )
    assert df.reset_index()[["group_id", "sku_name", "batch_id", "kg"]].equals(ground_truth)


# def test_boilling_plan_reader_corrupted_file(wb_corrupted: openpyxl.Workbook, batches: dict[str, int]) -> None:
#     reader = BoilingPlanReader(wb=wb_corrupted, first_batches=batches)
#     with pytest.raises(BoilingPlanReaderException):
#         _ = reader.parse()
