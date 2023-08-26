import pandas as pd

from app.enum import LineName
from app.imports.runtime import *
from app.models import *
from app.scheduler.boiling_plan import *

from .saturate import saturate_boiling_plan


def saturate_boiling_plan(boiling_plan_df: pd.DataFrame) -> pd.DataFrame:
    df = boiling_plan_df
    df["boiling"] = df["sku"].apply(lambda sku: utils.delistify(sku.made_from_boilings, single=True))
    df["boiling_key"] = df["boiling"].apply(lambda boiling: boiling.id)
    df["sku_cls_name"] = df["sku"].apply(lambda sku: str(sku.__class__))
    df["sku_name"] = df["sku"].apply(lambda sku: sku.name)

    def get_type(cls_name):
        if "Mascarpone" in cls_name:
            return "mascarpone"
        elif "CreamCheese" in cls_name:
            return "cream_cheese"

    df["group"] = df["sku_cls_name"].apply(get_type)
    df["is_cream"] = df["sku"].apply(lambda sku: "сливки" in sku.name.lower())

    return boiling_plan_df


def read_boiling_plan(wb_obj, as_boilings=True, first_batch_ids=None):
    """
    :param wb_obj: str or openpyxl.Workbook
    :return: pd.DataFrame(columns=['id', 'boiling', 'sku', 'kg'])
    """
    wb = utils.cast_workbook(wb_obj)
    first_batch_ids = first_batch_ids or {}

    dfs = []

    cur_id = 0

    for ws_name in ["План варок"]:
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
                "КГ Использовано",
            ]
        ]
        df.columns = [
            "group_id",
            "output",
            "sourdough_range",
            "sku",
            "kg",
        ]
        max_id = df["group_id"].max()
        df["group_id"] += cur_id
        cur_id += max_id
        dfs.append(df)

    df = pd.concat(dfs).reset_index(drop=True)
    df = df[df["sku"] != "-"]
    df["group_id"] = df["group_id"].astype(int)

    # batch_id and group_id are the same

    df["sku"] = df["sku"].apply(lambda sku: cast_model([MascarponeSKU, CreamCheeseSKU], sku))

    df = saturate_boiling_plan(df)

    if not as_boilings:
        return df

    # convert to boilings
    values = []
    for _, grp in df.groupby("group_id"):
        sourdough_range = str(grp.iloc[0]["sourdough_range"])

        if grp.iloc[0]["type"] == "mascarpone" and not grp.iloc[0]["is_cream"]:
            if sourdough_range == "1-2":
                proportion = [
                    500 + 300,
                    300 + 300,
                ]  # 500, 300, 300, 300 -> volumes of sourdougs
            else:
                proportion = [1] * len(grp.iloc[0]["sourdoughs"])
        else:
            proportion = [1]

        proportion = np.array(proportion)
        proportion = proportion / np.sum(proportion)

        sourdoughs = []

        for s in sourdough_range.split("-"):
            if s == "None" or utils.is_none(s) or not utils.is_int_like(s):
                assert (
                    grp.iloc[0]["type"] == "mascarpone" and grp.iloc[0]["is_cream"]
                ), "Для одной из варок не указаны заквасочники."
                sourdoughs.append("")
            else:
                sourdoughs.append(str(int(float(s))))

        total_boiling_volume = grp.iloc[0]["output"]

        assert abs(total_boiling_volume - grp["kg"].sum()) < 1e-5, "Указано неверное число килограмм в варке"

        boiling_volumes = list(proportion * total_boiling_volume)

        new_grp = utils.split_into_sum_groups(grp, boiling_volumes, column="kg", group_column="boiling_id")

        for i, (boiling_id, sub_grp) in enumerate(new_grp.groupby("boiling_id")):
            new_grp.loc[sub_grp.index, "sourdough"] = sourdoughs[i]

        if values:
            new_grp["boiling_id"] += values[-1]["boiling_id"] + 1
        values += new_grp.to_dict(orient="records")

    df = pd.DataFrame(values)

    with code("Get type"):

        def get_type(name):
            if "сливки" in name.lower():
                return "cream"
            elif "кремчиз" in name.lower():
                return "cream_cheese"
            elif "робиола" in name.lower():
                return "robiola"
            elif "творожный" in name.lower():
                return "cottage_cheese"
            elif "маскарпоне" in name.lower():
                return "mascarpone"
            else:
                raise Exception(
                    "Неизвестный тип максарпоне. В названии должен присутствовать один из типов: Сливки, Кремчиз, Робиола, Творожный, Маскарпоне"
                )

        df["full_type"] = df["sku"].apply(lambda sku: get_type(sku.name))

    df["batch_type"] = df["full_type"]

    df["batch_id"] = 0
    # set batch_id
    for batch_type in df["batch_type"].unique():
        cur_batch_id = 1
        for ind, grp in df[df["batch_type"] == batch_type].groupby("group_id"):
            df.loc[grp.index, "batch_id"] = cur_batch_id
            cur_batch_id += 1

    df = update_absolute_batch_id(df, first_batch_ids)
    return df
