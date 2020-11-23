from flask import  render_template, flash,  request
from . import main
from .. import db
from .. utils.excel_client import *
from .forms import RequestForm
from ..models import SKU
import pandas as pd
from io import BytesIO


# todo: разобраться с положительной заявкой. Идет ли она в сумму или нет
@main.route('/parse_request', methods=['GET', 'POST'])
def parse_request():
    form = RequestForm()
    result_list = []
    if request.method == 'POST' and form.validate_on_submit():
        date = form.date.data
        skus = db.session.query(SKU).all()

        group_items = [{
            "Ferment": x.boiling.ferment,
            "IsLactose": x.boiling.is_lactose,
            "Percent": x.boiling.percent,
            "FormFactor": x.form_factor
        } for x in skus.copy()]
        group_items = [dict(x) for x in set(frozenset(d.items()) for d in group_items)]

        file_bytes = request.files['input_file'].read()
        df = pd.read_excel(BytesIO(file_bytes), index_col=0)
        df_save = df.copy()
        df.columns = range(df.shape[1])
        df = df[df.loc['Дата выработки продукции:'].dropna().index]
        df = df.loc[['Дата выработки продукции:',
                     'Заявлено всего, кг:',
                     'Фактические остатки на складах - Заявлено, кг:',
                     'Нормативные остатки, кг']].fillna(0).iloc[:, :-1]
        data = list(zip(*df.values.tolist()))

        full_list = []
        sku_for_create = []
        for item in data:
            sku = [x for x in skus if x.name == item[0]]
            if sku is not None and len(sku) > 0:
                full_list.append({
                    "SKU": sku[0],
                    "Request": item[2]
                })
            else:
                sku_for_create.append(item[0])
        flash('No SKU: {}'.format(sku_for_create))

        for group_item in group_items:
            group_sku = [x for x in full_list if
                                 x["SKU"].boiling.ferment == group_item["Ferment"] and
                                 x["SKU"].boiling.is_lactose == group_item["IsLactose"] and
                                 x["SKU"].boiling.percent == group_item["Percent"] and
                                 x["SKU"].form_factor == group_item["FormFactor"]]
            if group_sku is not None:
                output_weight = group_sku[0]["SKU"].output_per_ton
                request_weight = sum([x["Request"] for x in group_sku if x["Request"] < 0])
                result_list.append({
                    "GroupSKU": group_sku,
                    "BoilingId": group_sku[0]["SKU"].boiling_id,
                    "BoilingCount": - request_weight / output_weight
                })

        result_path = build_plan(date, df_save, request_list=result_list)
        return render_template('parse_request.html', data=data, form=form, result_list=result_list, result_path=result_path)
    data = None
    result_list = None
    result_path = None
    return render_template('parse_request.html', data=data, form=form, result_list=result_list, result_path=result_path)
