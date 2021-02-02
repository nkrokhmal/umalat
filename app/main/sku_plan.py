from ..models_new import *
from flask import render_template, flash,  request, Markup
from . import main
from .forms import SkuPlanForm
from io import BytesIO
from app.utils.old.excel_client import *
from urllib.parse import quote
from app.utils.features.db_utils import *
from ..utils.sku_plan import *
from collections import namedtuple

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
    return Markup('В базе нет следующих SKU: <br> <br>' +
                  ' '.join(['<a href="/add_sku?name={0}">{1}</a> <br>'.format(quote(x), x) for x in sku]))


@main.route('/sku_plan', methods=['GET', 'POST'])
def sku_plan():
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
        return render_template('sku_plan.html', form=form, filename=sku_plan_client.filename)
    return render_template('sku_plan.html', form=form, filename=None)




