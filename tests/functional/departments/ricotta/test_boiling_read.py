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
            ["Сыр мягкий Рикотта массовой долей жира в сухом веществе 25%", 350 * 2, 2],
            ['Рикотта "Красная птица", 25%, 0,25 кг, пл/с', 350 * 2, 3],
            ['Рикотта "Aventino", 45%, 0,2 кг, п/с', 88, 4],
            ['Рикотта "Фермерская коллекция", 45%, 0,2 кг, пл/с', 168, 4],
            ['Рикотта "Pretto", 45%, 0,2 кг, пл/с', 644, 4],
            ['Рикотта "Pretto", 45%, 0,2 кг, пл/с', 450 * 2, 5],
            ['Рикотта "Pretto", 45%, 0,2 кг, пл/с', 450 * 2, 6],
            ['Рикотта "Pretto", 45%, 0,2 кг, пл/с', 450 * 2, 7],
            ['Рикотта "Pretto", 45%, 0,2 кг, пл/с', 450 * 2, 8],
            ['Рикотта "Unagrande", 50%, 0,5 кг, пл/с', 500 * 2, 9],
            ['Рикотта "Unagrande", 50%, 0,5 кг, пл/с', 500 * 2, 10],
            ['Рикотта с шоколадом "Бонджорно", 30%, 0,2 кг, пл/с', 250 * 2, 11],
            ["Рикотта с шоколадом «МАРКЕТ», 30%, 0,2 кг, п/с", 100 * 2, 11],
            ['Рикотта шоколадно-ореховая "Красная птица", 35%, 0,2 кг, пл/с', 100 * 2, 12],
            ['Рикотта шоколадно-ореховая "Бонджорно", 35%, 0,2 кг, пл/с', 250 * 2, 12],
        ],
        columns=["sku_name", "kg", "batch_id"],
    )
    assert (df[["sku_name", "kg", "batch_id"]] == ground_truth).all().all()
