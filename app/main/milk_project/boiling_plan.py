from app.imports.runtime import *
from app.utils.milk_project.boiling_plan_create import boiling_plan_create
from app.utils.milk_project.boiling_plan_draw import draw_boiling_plan
from app.utils.files.utils import move_boiling_file, save_boiling_plan
from app.utils.sku_plan import *
from app.utils.parse_remainings import *
from app.main import main
from app.models import *
from .forms import BoilingPlanForm


@main.route("/milk_project_boiling_plan", methods=["POST", "GET"])
@flask_login.login_required
def milk_project_boiling_plan():
    form = BoilingPlanForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        date = form.date.data
        skus = db.session.query(MilkProjectSKU).all()
        total_skus = db.session.query(SKU).all()
        boilings = db.session.query(MilkProjectBoiling).all()
        skus_req, remainings_df = parse_file(flask.request.files["input_file"].read())
        skus_req = get_skus(skus_req, skus, total_skus)
        skus_grouped = group_skus(skus_req, boilings)
        sku_plan_client = SkuPlanClient(
            date=date,
            remainings=remainings_df,
            skus_grouped=skus_grouped,
            template_path=flask.current_app.config["TEMPLATE_MILKPROJECT_BOILING_PLAN"],
        )
        sku_plan_client.fill_remainigs_list()
        sku_plan_client.fill_milk_project_sku_plan()

        excel_compiler, wb, wb_data_only, filename, filepath = move_boiling_file(
            sku_plan_client.date,
            sku_plan_client.filepath,
            sku_plan_client.filename,
            "милкпроджект",
        )
        sheet_name = flask.current_app.config["SHEET_NAMES"]["schedule_plan"]
        ws = wb_data_only[sheet_name]
        df, _ = parse_sheet(ws, sheet_name, excel_compiler, MilkProjectSKU)
        df_plan = boiling_plan_create(df)
        wb = draw_boiling_plan(df_plan, wb)
        save_boiling_plan(data=wb, filename=filename, date=sku_plan_client.date)
        return flask.render_template(
            "milk_project/boiling_plan.html", form=form, filename=filename, date=sku_plan_client.date,
        )
    form.date.data = datetime.today() + timedelta(days=1)
    return flask.render_template("milk_project/boiling_plan.html", form=form, filename=None)