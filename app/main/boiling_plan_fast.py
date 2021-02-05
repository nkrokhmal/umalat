from flask import render_template, request
from pycel import ExcelCompiler
from . import main
from .boiling_plan import parse_sheet
from .forms import SkuPlanForm
from .sku_plan import parse_file, get_skus, group_skus
from ..utils.boiling_plan_create import boiling_plan_create
from ..utils.boiling_plan_draw import draw_boiling_plan
from app.utils.old.generate_constructor import *
from ..utils.sku_plan import SkuPlanClient
from shutil import copyfile


def move_file(old_filepath, old_filename):
    new_filename = '{} План по варкам.xlsx'.format(old_filename.split(' ')[0])
    filepath = os.path.join(current_app.config['BOILING_PLAN_FOLDER'], new_filename)
    copyfile(old_filepath, filepath)
    excel_compiler = ExcelCompiler(filepath)
    wb_data_only = openpyxl.load_workbook(filename=filepath, data_only=True)
    wb = openpyxl.load_workbook(filename=filepath)
    return excel_compiler, wb, wb_data_only, new_filename, filepath


@main.route('/boiling_plan_fast', methods=['POST', 'GET'])
def boiling_plan_fast():
    form = SkuPlanForm()
    if request.method == 'POST' and form.validate_on_submit():
        date = form.date.data
        skus = db.session.query(SKU).all()
        boilings = db.session.query(Boiling).all()
        skus_req, remainings_df = parse_file(request.files['input_file'].read())
        skus_req = get_skus(skus_req, skus)
        skus_grouped = group_skus(skus_req, boilings)
        sku_plan_client = SkuPlanClient(
            date=date,
            remainings=remainings_df,
            skus_grouped=skus_grouped,
        )
        sku_plan_client.fill_remainigs_list()
        sku_plan_client.fill_schedule_list()

        excel_compiler, wb, wb_data_only, filename, filepath = move_file(
            sku_plan_client.filepath,
            sku_plan_client.filename
        )
        sheet_name = current_app.config['SHEET_NAMES']['schedule_plan']
        ws = wb_data_only[sheet_name]
        df, df_extra_packing = parse_sheet(ws, sheet_name, excel_compiler)
        df_plan = boiling_plan_create(df)
        wb = draw_boiling_plan(df_plan, df_extra_packing, wb)
        wb.save(filepath)
        return render_template('boiling_plan_fast.html', form=form, filename=filename)
    return render_template('boiling_plan_fast.html', form=form, filename=None)
