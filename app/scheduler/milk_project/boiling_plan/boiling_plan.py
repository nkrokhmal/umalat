from app.imports.runtime import *

from app.models import *
from app.enum import LineName

from .saturate import saturate_boiling_plan


def read_boiling_plan(wb_obj):
    """
    :param wb_obj: str or openpyxl.Workbook
    :return: pd.DataFrame(columns=['id', 'boiling', 'sku', 'kg'])
    """
    wb = utils.cast_workbook(wb_obj)

    cur_id = 0
    ws = wb["План варок"]

    values = []

    # collect header
    header = [ws.cell(1, i).value for i in range(1, 100) if ws.cell(1, i).value]

    for i in range(2, 200):
        if not ws.cell(i, 2).value:
            continue

        values.append([ws.cell(i, j).value for j in range(1, len(header) + 1)])

    df = pd.DataFrame(values, columns=header)
    df = df[
        [
            "Номер группы варок",
            "SKU",
            "КГ",
        ]
    ]
    df.columns = [
        "boiling_id",
        "sku",
        "kg",
    ]
    df = df[df["sku"] != "-"]
    df["boiling_id"] = df["boiling_id"].astype(int)

    df["sku"] = df["sku"].apply(lambda sku: cast_model(MilkProjectSKU, sku))

    df = saturate_boiling_plan(df)

    return df
