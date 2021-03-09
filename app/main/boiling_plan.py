from flask import render_template, request
from pycel import ExcelCompiler
from .forms import BoilingPlanForm
from ..utils.boiling_plan_create import boiling_plan_create
from ..utils.boiling_plan_draw import draw_boiling_plan
from app.utils.old.generate_constructor import *


REMAININGS_COLUMN = 4


def save_file(file):
    new_filename = "{} План по варкам.xlsx".format(file.filename.split(" ")[0])
    filepath = os.path.join(current_app.config["BOILING_PLAN_FOLDER"], new_filename)
    if file:
        file.save(filepath)
    excel_compiler = ExcelCompiler(filepath)
    wb_data_only = openpyxl.load_workbook(filename=filepath, data_only=True)
    wb = openpyxl.load_workbook(filename=filepath)
    return excel_compiler, wb, wb_data_only, new_filename, filepath


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
    df["sku"] = df["sku"].apply(cast_sku)
    df = df.replace(to_replace="None", value=np.nan).dropna()
    df["boiling_id"] = df["sku"].apply(lambda x: x.made_from_boilings[0].id)
    df["sku_id"] = df["sku"].apply(lambda x: x.id)
    df["plan"] = df["plan"].apply(lambda x: abs(float(x)))
    return df, df_extra_packing


@main.route("/boiling_plan", methods=["POST", "GET"])
def boiling_plan():
    form = BoilingPlanForm()
    if request.method == "POST" and form.validate_on_submit():
        file = request.files["input_file"]
        excel_compiler, wb, wb_data_only, filename, filepath = save_file(file)
        sheet_name = current_app.config["SHEET_NAMES"]["schedule_plan"]
        ws = wb_data_only[sheet_name]
        df, df_extra_packing = parse_sheet(ws, sheet_name, excel_compiler)
        df_plan = boiling_plan_create(df)
        wb = draw_boiling_plan(df_plan, df_extra_packing, wb)
        wb.save(filepath)
        return render_template("boiling_plan.html", form=form, filename=filename)
    return render_template("boiling_plan.html", form=form, filename=None)
