import io

from pathlib import Path

import flask
import openpyxl
import pandas as pd

from pytest import fixture

from app.utils.ricotta.boiling_plan_read import BoilingPlanReader


RICOTTA_TEST_DIR: Path = Path("app/data/tests/ricotta")


@fixture(scope="module")
def wb() -> openpyxl.Workbook:
    return openpyxl.load_workbook(RICOTTA_TEST_DIR / "boiling.xlsx", data_only=True)


@fixture(scope="module")
def first_batches() -> dict:
    return {"ricotta": 2}


def test_read_boiling_plan(wb: openpyxl.Workbook, first_batches: dict) -> None:
    df = BoilingPlanReader(wb=wb, first_batches=first_batches).parse()
    ground_truth = pd.DataFrame(
        [
            ["Сыр мягкий Рикотта массовой долей жира в сухом веществе 25%", 800, 2],
            ['Рикотта "Красная птица", 25%, 0,25 кг, пл/с', 800, 3],
            ['Рикотта "Aventino", 45%, 0,2 кг, п/с', 88, 4],
            ['Рикотта "Фермерская коллекция", 45%, 0,2 кг, пл/с', 168, 4],
            ['Рикотта "Pretto", 45%, 0,2 кг, пл/с', 744, 4],
            ['Рикотта "Pretto", 45%, 0,2 кг, пл/с', 1000, 5],
            ['Рикотта "Pretto", 45%, 0,2 кг, пл/с', 1000, 6],
            ['Рикотта "Pretto", 45%, 0,2 кг, пл/с', 1000, 7],
            ['Рикотта "Pretto", 45%, 0,2 кг, пл/с', 1000, 8],
            ['Рикотта "Unagrande", 50%, 0,5 кг, пл/с', 1100, 9],
            ['Рикотта "Unagrande", 50%, 0,5 кг, пл/с', 1100, 10],
            ['Рикотта с шоколадом "Бонджорно", 30%, 0,2 кг, пл/с', 600, 11],
            ["Рикотта с шоколадом «МАРКЕТ», 30%, 0,2 кг, п/с", 200, 11],
            ['Рикотта шоколадно-ореховая "Красная птица", 35%, 0,2 кг, пл/с', 200, 12],
            ['Рикотта шоколадно-ореховая "Бонджорно", 35%, 0,2 кг, пл/с', 600, 12],
        ],
        columns=["sku_name", "kg", "batch_id"],
    )
    assert (df[["sku_name", "kg", "batch_id"]] == ground_truth).all().all()
