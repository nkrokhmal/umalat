from flask import render_template, request
from .forms import BoilingPlanForm

from app.utils.mascarpone.boiling_plan_create import mascarpone_boiling_plan_create
from app.utils.mascarpone.boiling_plan_draw import draw_boiling_plan
from ...utils.sku_plan import *
from ...utils.parse_remainings import *
from .. import main


@main.route("/mascarpone_boiling_plan", methods=["POST", "GET"])
def mascarpone_boiling_plan():
    form = BoilingPlanForm(request.form)
    if request.method == "POST" and "submit" in request.form:
        date = form.date.data
        skus = db.session.query(MascarponeSKU).all()
        total_skus = db.session.query(SKU).all()
        boilings = db.session.query(MascarponeBoiling).all()

        file = request.files["input_file"]
        tmp_file_path = os.path.join(
            current_app.config["UPLOAD_TMP_FOLDER"], file.filename
        )

        if file:
            file.save(tmp_file_path)
        skus_req, remainings_df = parse_file_path(tmp_file_path)
        skus_req = get_skus(skus_req, skus, total_skus)
        skus_grouped = group_skus(skus_req, boilings)
        sku_plan_client = SkuPlanClient(
            date=date,
            remainings=remainings_df,
            skus_grouped=skus_grouped,
            template_path=current_app.config["TEMPLATE_MASCARPONE_BOILING_PLAN"],
        )
        sku_plan_client.fill_remainigs_list()
        sku_plan_client.fill_ricotta_sku_plan()

        excel_compiler, wb, wb_data_only, filename, filepath = move_file(
            sku_plan_client.filepath,
            sku_plan_client.filename,
            "рикотта",
        )
        sheet_name = current_app.config["SHEET_NAMES"]["schedule_plan"]
        ws = wb_data_only[sheet_name]
        df, _ = parse_sheet(ws, sheet_name, excel_compiler)
        df_plan = mascarpone_boiling_plan_create(df)
        print(df_plan)
        wb = draw_boiling_plan(df_plan, wb)
        wb.save(filepath)
        os.remove(tmp_file_path)
        return render_template(
            "mascarpone/boiling_plan.html", form=form, filename=filename
        )
    return render_template("mascarpone/boiling_plan.html", form=form, filename=None)
