from app.imports.runtime import *
from app.main import main
from app.models import *
from app.scheduler.mozzarella import *
from app.utils.files.utils import move_boiling_file, save_request
from app.utils.mozzarella.boiling_plan_create import boiling_plan_create
from app.utils.mozzarella.boiling_plan_draw import draw_boiling_plan
from app.utils.parse_remainings import *
from app.utils.sku_plan import *

from ...scheduler.mozzarella.to_boiling_plan.to_boiling_plan import to_boiling_plan
from .forms import BoilingPlanFastForm


@main.route("/mozzarella_boiling_plan", methods=["POST", "GET"])
@flask_login.login_required
def mozzarella_boiling_plan():
    form = BoilingPlanFastForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        date = form.date.data
        skus = db.session.query(MozzarellaSKU).all()
        total_skus = db.session.query(SKU).all()
        boilings = db.session.query(MozzarellaBoiling).all()

        file = flask.request.files["input_file"]
        skus_req, remainings_df = parse_file(file)
        yesterday_boiling_plan_df = pd.DataFrame()

        if "file_not_calculated" in flask.request.files:
            if flask.request.files["file_not_calculated"]:
                file_not_calculated = flask.request.files["file_not_calculated"]
                tmp_file_path = os.path.join(
                    flask.current_app.config["UPLOAD_TMP_FOLDER"], file_not_calculated.filename
                )
                if file_not_calculated:
                    file_not_calculated.save(tmp_file_path)

                wb_not_calculated = openpyxl.load_workbook(
                    filename=tmp_file_path,
                    data_only=True,
                )
                yesterday_boiling_plan_df = to_boiling_plan(wb_not_calculated, validate=False)[
                    ["sku_name", "original_kg"]
                ]
                yesterday_boiling_plan_df = yesterday_boiling_plan_df.groupby("sku_name").sum()

        skus_req = get_skus(skus_req, skus, total_skus)
        skus_grouped = group_skus(skus_req, boilings)
        sku_plan_client = SkuPlanClient(
            date=date,
            remainings=remainings_df,
            skus_grouped=skus_grouped,
            template_path=flask.current_app.config["TEMPLATE_MOZZARELLA_BOILING_PLAN"],
            yesterday_boiling_plan_df=yesterday_boiling_plan_df,
        )
        sku_plan_client.fill_remainings_list()
        sku_plan_client.fill_mozzarella_sku_plan()

        excel_compiler, wb, wb_data_only, filename, filepath = move_boiling_file(
            sku_plan_client.date,
            sku_plan_client.filepath,
            sku_plan_client.filename,
            "моцарелла",
        )
        sheet_name = flask.current_app.config["SHEET_NAMES"]["schedule_plan"]
        ws = wb_data_only[sheet_name]
        df, df_extra_packing = parse_sheet(ws, sheet_name, excel_compiler, MozzarellaSKU)
        df_plan = boiling_plan_create(df)
        wb = draw_boiling_plan(df_plan, df_extra_packing, wb)
        save_request(data=wb, filename=filename, date=sku_plan_client.date)
        return flask.render_template(
            "mozzarella/boiling_plan.html", form=form, filename=filename, date=sku_plan_client.date
        )

    form.date.data = datetime.today() + timedelta(days=1)
    return flask.render_template("mozzarella/boiling_plan.html", form=form, filename=None)
