import pandas as pd

from utils_ak.openpyxl import cast_workbook

from app.models import MozzarellaSKU, cast_model


def read_additional_packing(wb_obj):
    wb = cast_workbook(wb_obj)
    ws = wb["Дополнительная фасовка"]

    values = []
    for i in range(2, 10):
        if not ws.cell(i, 2).value:
            continue

        values.append([ws.cell(i, j).value for j in range(1, 3)])

    df = pd.DataFrame(values, columns=["sku", "kg"])
    df["sku_obj"] = df["sku"].apply(lambda sku: cast_model(MozzarellaSKU, sku))
    df["kg"] = -df["kg"]
    df = df[df["kg"] > 0]
    return df
