from utils_ak.interactive_imports import *
from app.schedule_maker.models import *
from app.enum import LineName
from .saturate import saturate_boiling_plan


def read_boiling_plan(wb_obj, saturate=True, normalization=True):
    """
    :param wb_obj: str or openpyxl.Workbook
    :return: pd.DataFrame(columns=['id', 'boiling', 'sku', 'kg'])
    """
    wb = cast_workbook(wb_obj)

    dfs = []

    for ws_name in ["Вода", "Соль"]:
        line = (
            cast_line(LineName.WATER) if ws_name == "Вода" else cast_line(LineName.SALT)
        )
        default_boiling_volume = line.output_ton

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
                "Тип варки",
                "Объем варки",
                "SKU",
                "КГ",
                "Форм фактор плавления",
                "Номер команды",
                "Конфигурация варки",
                "Вес варки",
                "Мойка",
            ]
        ]
        df.columns = [
            "boiling_params",
            "boiling_volume",
            "sku",
            "kg",
            "bff",
            "packing_team_id",
            "configuration",
            "total_volume",
            "cleaning",
        ]

        # fill group id
        df["group_id"] = (df["boiling_params"] == "-").astype(int).cumsum() + 1

        # fill total_volume
        df["total_volume"] = np.where(
            (df["sku"] == "-") & (df["total_volume"].isnull()),
            default_boiling_volume,
            df["total_volume"],
        )
        df["total_volume"] = df["total_volume"].fillna(method="bfill")

        # fill cleaning
        df["cleaning"] = np.where(
            (df["sku"] == "-") & (df["cleaning"].isnull()), "", df["cleaning"]
        )
        df["cleaning"] = df["cleaning"].fillna(method="bfill")
        df["cleaning"] = df["cleaning"].apply(
            lambda cleaning_type: {
                "Короткая мойка": "short",
                "Длинная мойка": "full",
            }.get(cleaning_type, "")
        )

        # fill configuration
        def format_configuration(value):
            if is_int_like(value):
                return str(int(value))
            elif value is None:
                return None
            elif np.isnan(value):
                return None
            elif isinstance(value, str):
                return value
            else:
                raise AssertionError("Unknown format")

        df["configuration"] = df["configuration"].apply(format_configuration)
        df["configuration"] = np.where(
            (df["sku"] == "-") & (df["configuration"].isnull()),
            "8000",
            df["configuration"],
        )
        df["configuration"] = df["configuration"].fillna(method="bfill")

        # remove separators and empty lines
        df = df[df["sku"] != "-"]
        df = df[~df["kg"].isnull()]

        # add line name to boiling_params
        df["boiling_params"] = line.name + "," + df["boiling_params"]
        dfs.append(df)

    # update salt group ids
    if len(dfs[0]) >= 1:
        dfs[1]["group_id"] += dfs[0].iloc[-1]["group_id"]

    df = pd.concat(dfs).reset_index(drop=True)
    df["sku"] = df["sku"].apply(cast_sku)

    df["boiling"] = df["boiling_params"].apply(cast_boiling)

    # set boiling form factors
    df["ff"] = df["sku"].apply(lambda sku: sku.form_factor)

    # # todo: hardcode, make properly
    # def _safe_cast_form_factor(obj):
    #     try:
    #         return cast_form_factor(obj)
    #     except:
    #         return None
    # df["bff"] = df["bff"].apply(_safe_cast_form_factor)

    # remove Терка from form_factors
    df["_bff"] = df["ff"].apply(lambda ff: ff if "Терка" not in ff.name else None)

    # fill Терка empty form factor values
    for idx, grp in df.copy().groupby("group_id"):
        if grp["_bff"].isnull().all():
            # take from bff input if not specified
            # todo: hardcode, make properly
            df.loc[grp.index, "_bff"] = cast_form_factor(8)  # 460
        else:
            filled_grp = grp.copy()
            filled_grp = filled_grp.fillna(method="ffill")
            filled_grp = filled_grp.fillna(method="bfill")
            df.loc[grp.index, "_bff"] = filled_grp["_bff"]
    df["bff"] = df["_bff"]

    # validate single boiling
    for idx, grp in df.groupby("group_id"):
        assert (
            len(grp["boiling"].unique()) == 1
        ), "В одной группе варок должен быть только один тип варки."

    # validate kilograms
    for idx, grp in df.groupby("group_id"):
        # todo: make common parameter
        if (
            abs(grp["kg"].sum() - grp.iloc[0]["total_volume"])
            / grp.iloc[0]["total_volume"]
            > 0.05
        ):
            raise AssertionError(
                "Одна из групп варок имеет неверное количество килограмм."
            )
        else:
            if normalization:
                if abs(grp["kg"].sum() - grp.iloc[0]["total_volume"]) > 1e-5:
                    # todo: warning message
                    df.loc[grp.index, "kg"] *= (
                        grp.iloc[0]["total_volume"] / grp["kg"].sum()
                    )  # scale to total_volume
                else:
                    # all fine
                    pass

    df = df[
        [
            "group_id",
            "sku",
            "kg",
            "packing_team_id",
            "boiling",
            "bff",
            "configuration",
            "cleaning",
        ]
    ]

    df = df.reset_index(drop=True)

    if saturate:
        df = saturate_boiling_plan(df)
    return df
