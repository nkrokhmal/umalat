from app.imports.runtime import *
from .forms import BoilingPlanForm
from app.utils.adygea.boiling_plan_create import boiling_plan_create
from app.utils.adygea.boiling_plan_draw import draw_boiling_plan
from app.utils.sku_plan import *
from app.utils.parse_remainings import *
from app.main import main
from app.utils.files.utils import move_boiling_file, save_boiling_plan
from app.models import *


@main.route("/adygea_boiling_plan", methods=["POST", "GET"])
@flask_login.login_required
def adygea_boiling_plan():
    form = BoilingPlanForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        date = form.date.data

        skus = db.session.query(AdygeaSKU).all()
        total_skus = db.session.query(SKU).all()
        boilings = db.session.query(AdygeaBoiling).all()

        file = flask.request.files["input_file"]
        tmp_file_path = os.path.join(
            flask.current_app.config["UPLOAD_TMP_FOLDER"], file.filename
        )

        if file:
            file.save(tmp_file_path)

        # skus_req, remainings_df = parse_file_path(tmp_file_path)
        skus_req, remainings_df = parse_file(file)
        skus_req = get_skus(skus_req, skus, total_skus)
        skus_grouped = group_skus(skus_req, boilings)
        sku_plan_client = SkuPlanClient(
            date=date,
            remainings=remainings_df,
            skus_grouped=skus_grouped,
            template_path=flask.current_app.config["TEMPLATE_ADYGEA_BOILING_PLAN"],
        )
        sku_plan_client.fill_remainigs_list()
        sku_plan_client.fill_adygea_sku_plan()

        excel_compiler, wb, wb_data_only, filename, filepath = move_boiling_file(
            sku_plan_client.date,
            sku_plan_client.filepath,
            sku_plan_client.filename,
            "адыгейский",
        )
        sheet_name = flask.current_app.config["SHEET_NAMES"]["schedule_plan"]
        ws = wb_data_only[sheet_name]
        df, _ = parse_sheet(ws, sheet_name, excel_compiler, AdygeaSKU)
        adygea_df = boiling_plan_create(df)
        wb = draw_boiling_plan(adygea_df, None, wb)
        save_boiling_plan(data=wb, filename=filename, date=sku_plan_client.date)
        os.remove(tmp_file_path)
        return flask.render_template(
            "adygea/boiling_plan.html", form=form, filename=filename, date=sku_plan_client.date
        )
    form.date.data = datetime.today() + timedelta(days=1)
    return flask.render_template("adygea/boiling_plan.html", form=form, filename=None)
