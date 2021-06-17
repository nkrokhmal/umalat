from app.imports.runtime import *

from urllib.parse import quote

from app.models import *
from app.utils.features.db_utils import *


REMAININGS_COLUMN = 4
COLUMNS = {
    "Date": "Дата выработки продукции:",
    "Total": "Заявлено всего, кг:",
    "Fact": "Фактические остатки на складах - Заявлено, кг:",
    "Normative": "Нормативные остатки, кг",
}


def parse_file(file_bytes):
    """
    :param file_bytes: файл остатков
    :return: преобразованный словарь с ключами Name, Total, Fact, Normative и изначальный
    файл остатков в виде Pandas DataFrame
    """
    df = pd.read_excel(io.BytesIO(file_bytes), index_col=0)
    df_original = df.copy()
    df = df[df.loc[COLUMNS["Date"]].dropna()[:-1].index]
    df = (
        df.loc[
            [COLUMNS["Date"], COLUMNS["Total"], COLUMNS["Fact"], COLUMNS["Normative"]]
        ]
        .fillna(0)
        .T
    )
    df.columns = ["Name", "Total", "Fact", "Norm"]
    return df.to_dict("records"), df_original


def parse_file_path(path):
    df = pd.read_excel(path, index_col=0)
    df_original = df.copy()
    df = df[df.loc[COLUMNS["Date"]].dropna()[:-1].index]
    df = (
        df.loc[
            [COLUMNS["Date"], COLUMNS["Total"], COLUMNS["Fact"], COLUMNS["Normative"]]
        ]
        .fillna(0)
        .T
    )
    df.columns = ["Name", "Total", "Fact", "Norm"]
    return df.to_dict("records"), df_original


def get_skus(skus_req, skus, total_skus):
    """
    :param skus_req: преобразованный словарь заявки
    :param skus: список sku текущего цеха
    :param total_skus: список всех sku в базе данных
    :return: Namedtuple название sku и план
    """
    result = []
    sku_for_creation = []
    for sku_req in skus_req:
        sku = get_sku_by_name(total_skus, sku_req["Name"])
        if sku:
            sku = get_sku_by_name(skus, sku_req["Name"])
            if sku:
                result.append(
                    collections.namedtuple("Plan", "sku, plan")(sku, sku_req["Fact"])
                )
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
        sku_grouped = [
            x for x in skus_req if x.sku.made_from_boilings[0].id == boiling.id
        ]
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
        return obj.line.output_ton
    elif isinstance(obj, RicottaSKU):
        return obj.made_from_boilings[0].number_of_tanks * obj.output_per_tank
    elif isinstance(obj, MascarponeSKU):
        return obj.made_from_boilings[0].boiling_technologies[0].output_ton
    elif isinstance(obj, CreamCheeseSKU):
        return obj.made_from_boilings[0].output_ton
    elif isinstance(obj, ButterSKU):
        return obj.line.output_kg
    elif isinstance(obj, MilkProjectSKU):
        return obj.made_from_boilings[0].output_kg
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
        + " ".join(
            ['<p class="mb-0"><small>{1}</small> </p>'.format(quote(x), x) for x in sku]
        )
    )


def parse_sheet(ws, sheet_name, excel_compiler):
    values = []
    for i in range(1, ws.max_row + 1):
        if ws.cell(i, REMAININGS_COLUMN):
            values.append(
                [
                    excel_compiler.evaluate(
                        "'{}'!{}".format(sheet_name, ws.cell(i, j).coordinate)
                    )
                    for j in range(4, 9)
                ]
            )

    df = pd.DataFrame(values[1:])
    df.columns = [
        "sku",
        "remainings - request",
        "normative remainings",
        "plan",
        "extra_packing",
    ]
    df_extra_packing = df[["sku", "extra_packing"]].copy()
    df = df.fillna(0)
    df = df[df["plan"] != 0]
    df = df[
        df["plan"].apply(lambda x: type(x) == int or type(x) == float or x.isnumeric())
    ]
    df = df[["sku", "plan"]]
    df["sku"] = df["sku"].apply(lambda x: cast_sku_name(x))
    df = df.replace(to_replace="None", value=np.nan).dropna()
    df["boiling_id"] = df["sku"].apply(lambda x: x.made_from_boilings[0].id)
    df["sku_id"] = df["sku"].apply(lambda x: x.id)
    df["plan"] = df["plan"].apply(lambda x: abs(float(x)))
    return df, df_extra_packing


def move_file(old_filepath, old_filename, department=""):
    new_filename = "{} План по варкам {}.xlsx".format(
        old_filename.split(" ")[0], department
    )
    filepath = os.path.join(flask.current_app.config["BOILING_PLAN_FOLDER"], new_filename)
    shutil.copyfile(old_filepath, filepath)
    excel_compiler = pycel.ExcelCompiler(filepath)
    wb_data_only = openpyxl.load_workbook(filename=filepath, data_only=True)
    wb = openpyxl.load_workbook(filename=filepath)
    return excel_compiler, wb, wb_data_only, new_filename, filepath
