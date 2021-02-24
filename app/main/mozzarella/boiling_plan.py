from io import BytesIO
from urllib.parse import quote
from flask import render_template, request, flash, Markup
from pycel import ExcelCompiler
from .. import main
from .forms import BoilingPlanFastForm
from ...utils.boiling_plan_create import boiling_plan_create
from ...utils.boiling_plan_draw import draw_boiling_plan
from ...utils.sku_plan import *
from app.utils.features.db_utils import *
from shutil import copyfile
from flask import current_app
from app.interactive_imports import *
from collections import namedtuple


REMAININGS_COLUMN = 4
COLUMNS = {
    'Date': 'Дата выработки продукции:',
    'Total': 'Заявлено всего, кг:',
    'Fact': 'Фактические остатки на складах - Заявлено, кг:',
    'Normative': 'Нормативные остатки, кг'
}


def parse_file(file_bytes):
    df = pd.read_excel(BytesIO(file_bytes), index_col=0)
    df_original = df.copy()
    df = df[df.loc[COLUMNS['Date']].dropna()[:-1].index]
    df = df.loc[[COLUMNS['Date'], COLUMNS['Total'], COLUMNS['Fact'], COLUMNS['Normative']]].fillna(0).T
    df.columns = ['Name', 'Total', 'Fact', 'Norm']
    return df.to_dict('records'), df_original


def get_skus(skus_req, skus):
    result = []
    sku_for_creation = []
    for sku_req in skus_req:
        sku = get_sku_by_name(skus, sku_req['Name'])
        if sku is not None:
            result.append(namedtuple('Plan', 'sku, plan')(sku, sku_req['Fact']))
        elif sku_req['Name'] not in current_app.config['IGNORE_SKUS']:
            sku_for_creation.append(sku_req['Name'])
        else:
            pass
    if sku_for_creation:
        flash(convert_sku(sku_for_creation))
    return result


def group_skus(skus_req, boilings):
    result = []
    for boiling in boilings:
        sku_grouped = [x for x in skus_req if x.sku.made_from_boilings[0].id == boiling.id]
        if any(sku_grouped):
            Request = namedtuple('Request', 'skus, boiling, volume')
            result.append(
                Request(
                    sku_grouped,
                    boiling,
                    sku_grouped[0].sku.line.output_ton,
                )
            )
    return result


def convert_sku(sku):
    return Markup(' '.join(['<a href="/add_sku?name={0}">{1}</a> <br>'.format(quote(x), x) for x in sku]))


def parse_sheet(ws, sheet_name, excel_compiler):
    values = []
    for i in range(1, ws.max_row + 1):
        if ws.cell(i, REMAININGS_COLUMN):
            values.append([excel_compiler.evaluate("'{}'!{}".format(
                sheet_name,
                ws.cell(i, j).coordinate)) for j in range(4, 9)])
    df = pd.DataFrame(values[1:])
    df.columns = ['sku', 'remainings - request', 'normative remainings', 'plan', 'extra_packing']
    df_extra_packing = df[['sku', 'extra_packing']].copy()
    df = df.fillna(0)
    df = df[df['plan'] != 0]
    df = df[df['plan'].apply(lambda x: type(x) == int or type(x) == float or x.isnumeric())]
    df = df[['sku', 'plan']]
    df['sku'] = df['sku'].apply(cast_sku)
    df = df.replace(to_replace='None', value=np.nan).dropna()
    df['boiling_id'] = df['sku'].apply(lambda x: x.made_from_boilings[0].id)
    df['sku_id'] = df['sku'].apply(lambda x: x.id)
    df['plan'] = df['plan'].apply(lambda x: abs(float(x)))
    return df, df_extra_packing


def move_file(old_filepath, old_filename):
    new_filename = '{} План по варкам.xlsx'.format(old_filename.split(' ')[0])
    filepath = os.path.join(current_app.config['BOILING_PLAN_FOLDER'], new_filename)
    copyfile(old_filepath, filepath)
    excel_compiler = ExcelCompiler(filepath)
    wb_data_only = openpyxl.load_workbook(filename=filepath, data_only=True)
    wb = openpyxl.load_workbook(filename=filepath)
    return excel_compiler, wb, wb_data_only, new_filename, filepath


@main.route('/boiling_plan', methods=['POST', 'GET'])
def boiling_plan():
    form = BoilingPlanFastForm(request.form)
    if request.method == 'POST' and 'submit' in request.form:
        date = form.date.data
        skus = db.session.query(MozzarellaSKU).all()
        boilings = db.session.query(MozzarellaBoiling).all()
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
        return render_template('mozzarella/boiling_plan.html', form=form, filename=filename)
    return render_template('mozzarella/boiling_plan.html', form=form, filename=None)
