from utils_ak.interactive_imports import *
from app.schedule_maker.models import *
from app.enum import LineName
from .saturate import saturate_boiling_plan

# todo: normalization
# todo: rounding


def read_boiling_plan(wb_obj, as_boilings=True):
    """
    :param wb_obj: str or openpyxl.Workbook
    :return: pd.DataFrame(columns=['id', 'boiling', 'sku', 'kg'])
    """
    wb = cast_workbook(wb_obj)

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
            "batch_id",
            "output",
            "sourdough_range",
            "sku",
            "kg",
        ]
        max_id = df["batch_id"].max()
        df["batch_id"] += cur_id
        cur_id += max_id
        dfs.append(df)

    df = pd.concat(dfs).reset_index(drop=True)
    df = df[df["sku"] != "-"]
    df["batch_id"] = df["batch_id"].astype(int)

    df["sku"] = df["sku"].apply(
        lambda sku: cast_model([MascarponeSKU, CreamCheeseSKU], sku)
    )

    df = saturate_boiling_plan(df)

    if not as_boilings:
        return df

    # convert to boilings
    values = []
    for boiling_id, grp in df.groupby("batch_id"):
        sourdough_range = str(grp.iloc[0]["sourdough_range"])

        if grp.iloc[0]["type"] == "mascarpone" and not grp.iloc[0]["is_cream"]:
            if sourdough_range == "1-2":
                proportion = [800, 600]
            else:
                proportion = [1] * len(grp.iloc[0]["sourdoughs"])
        else:
            proportion = [1]

        proportion = np.array(proportion)
        proportion = proportion / np.sum(proportion)

        sourdoughs = []
        for s in sourdough_range.split("-"):
            if s == "None" or np.isnan(s):
                assert (
                    grp.iloc[0]["type"] == "mascarpone" and grp.iloc[0]["is_cream"]
                ), "Для одной из варок не указаны заквасочники."
                sourdoughs.append("")
            else:
                sourdoughs.append(str(int(float(s))))

        total_boiling_volume = grp.iloc[0]["output"]

        assert (
            abs(total_boiling_volume - grp["kg"].sum()) < 1e-5
        ), "Указано неверное число килограмм в варке"

        boiling_volumes = list(proportion * total_boiling_volume)

        new_grp = split_into_sum_groups(
            grp, boiling_volumes, column="kg", group_column="boiling_id"
        )

        for i, (boiling_id, sub_grp) in enumerate(new_grp.groupby("boiling_id")):
            new_grp.loc[sub_grp.index, "sourdough"] = sourdoughs[i]

        if values:
            new_grp["boiling_id"] += values[-1]["boiling_id"] + 1
        values += new_grp.to_dict(orient="records")

    df = pd.DataFrame(values)
    return df
