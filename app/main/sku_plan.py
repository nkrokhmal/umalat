from ..models import *
from flask import render_template, flash,  request, current_app
from . import main
from .forms import RequestForm
from io import BytesIO
from .. utils.excel_client import *



COLUMNS = {
    'Date': 'Дата выработки продукции:',
    'Total': 'Заявлено всего, кг:',
    'Fact': 'Фактические остатки на складах - Заявлено, кг:',
    'Normative': 'Нормативные остатки, кг'
}


@main.route('/sku_plan', methods=['GET', 'POST'])
def sku_plan():
    form = RequestForm()
    if request.method == 'POST' and form.validate_on_submit():
        result_list = []
        date = form.date.data
        skus = db.session.query(SKU).all()

        group_items = [{'BoilingId': x.boilings[0].id} for x in skus.copy()]
        group_items = [dict(x) for x in set(frozenset(d.items()) for d in group_items)]

        file_bytes = request.files['input_file'].read()
        df = pd.read_excel(BytesIO(file_bytes), index_col=0)
        df_save = df.copy()
        df.columns = range(df.shape[1])
        df = df[df.loc[COLUMNS['Date']].dropna().index]
        df = df.loc[[COLUMNS['Date'], COLUMNS['Total'], COLUMNS['Fact'], COLUMNS['Normative']]].fillna(0).iloc[:, :-1]
        data = list(zip(*df.values.tolist()))

        full_list = []
        sku_for_create = []
        for item in data:
            sku = [x for x in skus if x.name == item[0]]
            if sku is not None and len(sku) > 0:
                full_list.append({
                    'SKU': sku[0],
                    'Request': item[2]
                })
            else:
                sku_for_create.append(item[0])
        # flash('No SKU: {}'.format(sku_for_create))

        for group_item in group_items:
            group_sku = [x for x in full_list if
                         x['SKU'].boilings[0].id == group_item['BoilingId']]
            if len(group_sku) > 0:
                # todo: вынести выход с тонны в параметры линии
                output_weight = group_sku[0]['SKU'].output_per_ton
                request_weight = sum([x['Request'] for x in group_sku if x['Request'] < 0])
                result_list.append({
                    'GroupSKU': group_sku,
                    'BoilingId': group_sku[0]['SKU'].boilings[0].id,
                    'BoilingCount': - request_weight / output_weight,
                    'Volume': group_sku[0]['SKU'].output_per_ton,
                    'IsLactose': group_sku[0]['SKU'].boilings[0].is_lactose
                })

        file_name = build_plan_sku(date, df_save, request_list=result_list)
        data = [x for x in data if type(x[1]) is not str]
        return render_template('sku_plan.html', data=data, form=form, result_list=result_list,
                               file_name=file_name)
    data = None
    result_list = None
    file_name = None
    return render_template('sku_plan.html', data=data, form=form, result_list=result_list, file_name=file_name)
