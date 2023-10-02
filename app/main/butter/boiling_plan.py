from app.imports.runtime import *
from app.main import main
from app.models import *
from app.utils.butter.boiling_plan_create import butter_boiling_plan_create
from app.utils.butter.boiling_plan_draw import draw_boiling_plan
from app.utils.files.utils import move_boiling_file, save_request
from app.utils.parse_remainings import *
from app.utils.sku_plan import *

from .forms import BoilingPlanForm


@main.route("/butter_boiling_plan", methods=["POST", "GET"])
@flask_login.login_required
def butter_boiling_plan():
    # - Create form

    form = BoilingPlanForm(flask.request.form)

    # - Process POST

    if flask.request.method == "POST" and "submit" in flask.request.form:
        # - Get form data

        date = form.date.data
        file = flask.request.files["input_file"]

        # - Get data from db

        skus = db.session.query(ButterSKU).all()
        total_skus = db.session.query(SKU).all()
        boilings = db.session.query(ButterBoiling).all()

        # - Create plan

        skus_req, remainings_df = parse_file(file)
        skus_req = get_skus(skus_req, skus, total_skus)
        skus_grouped = group_skus(skus_req, boilings)
        sku_plan_client = SkuPlanClient(
            date=date,
            remainings=remainings_df,
            skus_grouped=skus_grouped,
            template_path=flask.current_app.config["TEMPLATE_BUTTER_BOILING_PLAN"],
        )
        sku_plan_client.fill_remainings_list()
        sku_plan_client.fill_butter_sku_plan()

        excel_compiler, wb, wb_data_only, filename, filepath = move_boiling_file(
            sku_plan_client.date,
            sku_plan_client.filepath,
            sku_plan_client.filename,
            "масло",
        )
        sheet_name = flask.current_app.config["SHEET_NAMES"]["schedule_plan"]
        ws = wb_data_only[sheet_name]
        df, _ = parse_sheet(ws, sheet_name, excel_compiler)
        df_plan = butter_boiling_plan_create(df)

        # - Draw plan

        wb = draw_boiling_plan(df_plan, wb)

        # - Save request

        save_request(data=wb, filename=filename, date=sku_plan_client.date)

        # - Render template

        return flask.render_template(
            "butter/boiling_plan.html", form=form, filename=filename, date=sku_plan_client.date
        )

    # - Process GET

    form.date.data = datetime.today() + timedelta(days=1)

    return flask.render_template("butter/boiling_plan.html", form=form, filename=None)
