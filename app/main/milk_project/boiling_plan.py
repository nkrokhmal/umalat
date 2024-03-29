from app.imports.runtime import *
from app.main import main
from app.models import *
from app.utils.adygea.boiling_plan_create import boiling_plan_create as boiling_plan_create_adygea
from app.utils.adygea.boiling_plan_draw import draw_boiling_plan as draw_boiling_plan_adygea
from app.utils.brynza.boiling_plan_create import boiling_plan_create as boiling_plan_create_brynza
from app.utils.brynza.boiling_plan_draw import draw_boiling_plan as draw_boiling_plan_brynza
from app.utils.files.utils import move_boiling_file, save_request
from app.utils.milk_project.boiling_plan_create import boiling_plan_create as boiling_plan_create_milk_project
from app.utils.milk_project.boiling_plan_draw import draw_boiling_plan as draw_boiling_plan_milk_project
from app.utils.parse_remainings import *
from app.utils.sku_plan import *

from .forms import BoilingPlanForm


@main.route("/milk_project_boiling_plan", methods=["POST", "GET"])
@flask_login.login_required
def milk_project_boiling_plan():
    form = BoilingPlanForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        date = form.date.data
        skus, boilings, total_skus = [], [], db.session.query(SKU).all()
        for sku_type, boiling_type in zip(
            [MilkProjectSKU, AdygeaSKU, BrynzaSKU],
            [MilkProjectBoiling, AdygeaBoiling, BrynzaBoiling],
        ):
            skus += db.session.query(sku_type).all()
            boilings += db.session.query(boiling_type).all()

        file = flask.request.files["input_file"]
        skus_req, remainings_df = parse_file(file)

        skus_req = get_skus(skus_req, skus, total_skus)
        skus_grouped = group_skus(skus_req, boilings)
        sku_plan_client = SkuPlanClient(
            date=date,
            remainings=remainings_df,
            skus_grouped=skus_grouped,
            template_path=flask.current_app.config["TEMPLATE_MILKPROJECT_BOILING_PLAN"],
        )
        sku_plan_client.fill_remainings_list()
        sku_plan_client.fill_milk_project_sku_plan()

        excel_compiler, wb, wb_data_only, filename, filepath = move_boiling_file(
            sku_plan_client.date,
            sku_plan_client.filepath,
            sku_plan_client.filename,
            "милкпроджект",
        )
        sheet_name = flask.current_app.config["SHEET_NAMES"]["schedule_plan"]
        ws = wb_data_only[sheet_name]
        df, _ = parse_sheet(ws, sheet_name, excel_compiler, SKU)

        milk_project_df = df[df["sku"].apply(lambda x: isinstance(x, MilkProjectSKU))]
        adygea_df = df[df["sku"].apply(lambda x: isinstance(x, AdygeaSKU))]
        brynza_df = df[df["sku"].apply(lambda x: isinstance(x, BrynzaSKU))]

        df_plan_milk_project = boiling_plan_create_milk_project(milk_project_df)
        df_plan_adygea = boiling_plan_create_adygea(adygea_df)
        df_plan_brynza = boiling_plan_create_brynza(brynza_df)

        wb = draw_boiling_plan_milk_project(df_plan_milk_project, wb)
        wb = draw_boiling_plan_adygea(df_plan_adygea, wb)
        wb = draw_boiling_plan_brynza(df_plan_brynza, wb)

        save_request(data=wb, filename=filename, date=sku_plan_client.date)
        return flask.render_template(
            "milk_project/boiling_plan.html",
            form=form,
            filename=filename,
            date=sku_plan_client.date,
        )
    form.date.data = datetime.today() + timedelta(days=1)
    return flask.render_template("milk_project/boiling_plan.html", form=form, filename=None)
