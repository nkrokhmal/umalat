import collections
import io
import os
import typing as tp

from copy import deepcopy
from urllib.parse import quote

import flask
import numpy as np
import pandas as pd

from app.globals import db
from app.models import SKU, AdygeaSKU, BrynzaSKU, ButterSKU, MascarponeSKU, MilkProjectSKU, MozzarellaSKU, RicottaSKU
from app.utils.features.db_utils import get_sku_by_name


REMAININGS_COLUMN: int = 4
COLUMNS: dict[str, str] = {
    "Date": "Дата выработки продукции:",
    "Total": "Заявлено всего, кг:",
    "Fact": "Фактические остатки на складах - Заявлено, кг:",
    "Normative": "Нормативные остатки, кг",
    "Code": "Код номенклатуры в 1C",
}


def string_to_float(x: str) -> float:
    try:
        return float(x)
    except:
        res = x.replace(",", ".").replace(" ", "").replace("\xa0", "")
        return float(res)


def parse_df(df: pd.DataFrame, mode: tp.Literal["csv", "excel"]) -> tuple[dict, pd.DataFrame]:
    match mode:
        case "csv":
            df.columns = [COLUMNS["Code"], COLUMNS["Date"], COLUMNS["Fact"]]
            df[COLUMNS["Normative"]] = 0
            df[COLUMNS["Total"]] = 0

            df = df[[COLUMNS["Date"], COLUMNS["Code"], COLUMNS["Fact"], COLUMNS["Normative"], COLUMNS["Total"]]]
            df[COLUMNS["Fact"]] = df[COLUMNS["Fact"]].apply(lambda x: string_to_float(x))

            df_original = deepcopy(df).T
            zero_df = pd.DataFrame(3 * [[""] * df_original.shape[1]])
            zero_df.columns = df_original.columns

            df_original = pd.concat([zero_df, df_original])

            df_dict = deepcopy(df)
            df_dict = df_dict[[COLUMNS["Date"], COLUMNS["Total"], COLUMNS["Fact"], COLUMNS["Normative"]]]
            df_dict.columns = ["Name", "Total", "Fact", "Norm"]
            return df_dict.to_dict("records"), df_original
        case "xlsx":
            df_original = deepcopy(df)

            if df.index[0] == "Отчет от" or len(df.index) > 150:
                df = df[df.loc[COLUMNS["Date"]].dropna()[:-1].index]
                df = df.loc[[COLUMNS["Date"], COLUMNS["Total"], COLUMNS["Fact"], COLUMNS["Normative"]]].fillna(0).T
                df.columns = ["Name", "Total", "Fact", "Norm"]
                return df.to_dict("records"), df_original

            else:
                df = df.loc[[COLUMNS["Date"], COLUMNS["Total"], COLUMNS["Fact"], COLUMNS["Normative"]]].fillna(0).T
                df.columns = ["Name", "Total", "Fact", "Norm"]
                df["Fact"] = df["Fact"].apply(lambda x: (string_to_float(x)))
                df_original.loc[COLUMNS["Fact"]] = df["Fact"]

                if list(df_original.index).index(COLUMNS["Date"]) == 2:
                    zero_df = pd.DataFrame(["-"] * df_original.shape[1]).T
                    zero_df.columns = df_original.columns
                    df_original = pd.concat([zero_df, df_original])

                return df.to_dict("records"), df_original


def parse_file(file):
    """
    :param file_bytes: файл остатков
    :return: преобразованный словарь с ключами Name, Total, Fact, Normative и изначальный
    файл остатков в виде Pandas DataFrame
    """
    file_bytes = file.read()
    filename = file.filename

    if filename.split(".")[-1] == "csv":
        df = pd.read_csv(io.BytesIO(file_bytes), sep=";")
        return parse_df(df, "csv")
    else:
        df = pd.read_excel(io.BytesIO(file_bytes), index_col=0)
        return parse_df(df, "xlsx")


def parse_file_path(path: os.PathLike | str) -> tuple[dict, pd.DataFrame]:
    mode = str(path).split(".")[-1]
    if mode == "csv":
        return parse_df(pd.read_csv(path, sep=";"), "csv")
    else:
        return parse_df(pd.read_excel(path, index_col=0), "xlsx")


def get_skus(skus_req: list[dict], skus: list[SKU], total_skus: list[SKU]) -> list[collections.namedtuple]:
    """
    :param skus_req: преобразованный словарь заявки
    :param skus: список sku текущего цеха
    :param total_skus: список всех sku в базе данных
    :return: Namedtuple название sku и план
    """
    result = []
    sku_for_creation = []

    for sku_req in skus_req:
        sku_req["Name"] = "".join(sku_req["Name"].splitlines())
        sku = get_sku_by_name(total_skus, sku_req["Name"])
        if sku:
            sku = get_sku_by_name(skus, sku_req["Name"])
            if sku:
                result.append(collections.namedtuple("Plan", "sku, plan")(sku, sku_req["Fact"]))
        else:
            if sku_req["Name"] not in flask.current_app.config["IGNORE_SKUS"]:
                sku_for_creation.append(sku_req["Name"])

    if sku_for_creation:
        flask.flash(convert_sku(sku_for_creation), "warning")
    return result


def group_skus(skus_req, boilings):
    """
    :param skus_req:
    :param boilings:
    :return:
    """
    result = []
    for boiling in boilings:
        boiling.to_str()
        sku_grouped = [x for x in skus_req if x.sku.made_from_boilings[0].id == boiling.id]
        if any(sku_grouped):
            Request = collections.namedtuple("Request", "skus, boiling, volume")
            result.append(
                Request(
                    sku_grouped,
                    boiling,
                    cast_volume(sku_grouped[0].sku),
                )
            )
    return result


def cast_volume(obj):
    if isinstance(obj, MozzarellaSKU):
        return obj.line.output_kg
    elif isinstance(obj, RicottaSKU):
        return obj.made_from_boilings[0].output_kg
    elif isinstance(obj, MascarponeSKU):
        b = obj.made_from_boilings[0]
        return round(b.input_kg * b.output_coeff, -1) + b.output_constant
    elif isinstance(obj, ButterSKU):
        return obj.line.output_kg
    elif isinstance(obj, MilkProjectSKU):
        return obj.made_from_boilings[0].output_kg
    elif isinstance(obj, AdygeaSKU):
        return obj.made_from_boilings[0].output_kg
    elif isinstance(obj, BrynzaSKU):
        return 1000
    else:
        raise Exception("Unknown sku type")


def cast_sku_name(obj):
    if isinstance(obj, SKU):
        return obj
    elif isinstance(obj, (str, int)):
        obj = str(obj)
        result = db.session.query(SKU).filter(SKU.name == obj).first()
        return result
    else:
        raise Exception("Unknown sku type")


def convert_sku(sku):
    return flask.Markup(
        "В базе нет следующих SKU: <br> <br>"
        + " ".join(['<p class="mb-0"><small>{1}</small> </p>'.format(quote(x), x) for x in sku])
    )


def parse_sheet(ws, sheet_name, excel_compiler, sku_type=ButterSKU):
    values = []
    for i in range(1, ws.max_row + 1):
        if ws.cell(i, REMAININGS_COLUMN):
            values.append(
                [excel_compiler.evaluate("'{}'!{}".format(sheet_name, ws.cell(i, j).coordinate)) for j in range(4, 10)]
            )

    df = pd.DataFrame(values[1:])
    df.columns = [
        "sku",
        "remainings - request",
        "normative remainings",
        "not_calculated",
        "plan",
        "extra_packing",
    ]
    df_extra_packing = df[["sku", "extra_packing"]].copy()
    df = df.fillna(0)
    df = df[df["plan"] != 0]
    if sku_type == ButterSKU:
        df = df.iloc[0:0]
        skus = db.session.query(sku_type).all()
        for sku in skus:
            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        [
                            {
                                "sku": sku,
                                "remainings - request": 0,
                                "normative remainings": 0,
                                "plan": sku.line.output_kg,
                                "extra_packing": 0,
                            },
                        ]
                    ),
                ],
                ignore_index=True,
            )
    else:
        if df.empty:
            sku = db.session.query(sku_type).all()[0]
            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        [
                            {
                                "sku": sku,
                                "remainings - request": 0,
                                "normative remainings": 0,
                                "plan": 1,
                                "extra_packing": 0,
                            }
                        ]
                    ),
                ],
                ignore_index=True,
            )
            flask.flash("Заявка на текущий день нулевая!")
    df = df[df["plan"].apply(lambda x: type(x) == int or type(x) == float or x.isnumeric())]
    df = df[["sku", "plan"]]
    df["sku"] = df["sku"].apply(lambda x: cast_sku_name(x))
    df = df.replace(to_replace="None", value=np.nan).dropna()
    df["boiling_id"] = df["sku"].apply(lambda x: x.made_from_boilings[0].id)
    df["sku_id"] = df["sku"].apply(lambda x: x.id)
    df["plan"] = df["plan"].apply(lambda x: abs(float(x)))
    return df, df_extra_packing


__all__ = [
    "parse_df",
    "parse_file",
    "parse_file_path",
    "get_skus",
    "group_skus",
    "cast_volume",
    "cast_sku_name",
    "convert_sku",
    "parse_sheet",
]
