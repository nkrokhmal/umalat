from utils_ak.interactive_imports import *
from app.schedule_maker.models import *
from app.enum import LineName
from .saturate import saturate_boiling_plan

# todo: normalization


def read_boiling_plan(wb_obj, as_boilings=True):
    """
    :param wb_obj: str or openpyxl.Workbook
    :return: pd.DataFrame(columns=['id', 'boiling', 'sku', 'kg'])
    """
    wb = cast_workbook(wb_obj)

    dfs = []

    cur_id = 0
    for ws_name in ["Маскарпоне", "Крем чиз", "Сливки", "План варок"]:
        if ws_name not in wb.sheetnames:
            continue
        ws = wb[ws_name]
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
                "Выход с одной варки, кг",
                "Заквасочники",
                "SKU",
                "КГ",
            ]
        ]
        df.columns = [
            "batch_id",
            "output",
            "sourdough",
            "sku",
            "kg",
        ]
        max_id = df["batch_id"].max()
        df["batch_id"] += cur_id
        cur_id += max_id
        dfs.append(df)

    df = pd.concat(dfs).reset_index(drop=True)
    df = df[df["sku"] != "-"]
    df["sku"] = df["sku"].apply(
        lambda sku: cast_model([MascarponeSKU, CreamCheeseSKU], sku)
    )

    if not as_boilings:
        return df

    # convert to boilings
    values = []
    for boiling_id, grp in df.groupby("batch_id"):
        sourdough = grp.iloc[0]["sourdough"]
        if sourdough == "1-2":
            proportion = [800, 600]
        elif "-" in sourdough:
            proportion = [1, 1]
        else:
            proportion = [1]
        proportion = np.array(proportion)
        proportion = proportion / np.sum(proportion)

        total_boiling_volume = grp.iloc[0]["output"]
        boiling_volumes = list(proportion * total_boiling_volume)

        for i, boiling_volume in enumerate(boiling_volumes):
            left = boiling_volume
            for j, row in grp.iterrows():
                while left > 1e-5:
                    pass


        values += grp.tolist()

    return df
