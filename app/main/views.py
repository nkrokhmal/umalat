from flask import session, url_for, render_template, flash, request, make_response, current_app, request
from flask import jsonify
from werkzeug.utils import redirect
from . import main
from .. import db
from .. utils.excel_client import *
from .forms import PouringProcessForm, BoilingForm, RequestForm
from ..models import SKU, Boiling, GlobalPouringProcess, Melting, Pouring, Line, Termizator, Packer,\
    Departmenent
import pandas as pd
from io import BytesIO
import os
from datetime import datetime


@main.route('/')
def index():
    lines = db.session.query(Line).all()
    packers = db.session.query(Packer).all()
    termizators = db.session.query(Termizator).all()
    departments = db.session.query(Departmenent).all()
    return render_template('index.html', lines=lines, packers=packers, termizators=termizators, departments=departments)


@main.route('/delete_sku/<int:sku_id>', methods=['DELETE'])
def delete_sku(sku_id):
    sku = db.session.query(SKU).get_or_404(sku_id)
    if sku:
        db.session.delete(sku)
        db.session.commit()
    return redirect(url_for('.get_sku'))


@main.route('/add_pouring_process', methods=['POST', 'GET'])
def add_pouring_process():
    form = PouringProcessForm()
    if form.validate_on_submit():
        pouring_process = GlobalPouringProcess(
            pouring_time=form.pouring_time.data
        )
        db.session.add(pouring_process)
        db.session.commit()
        return redirect(url_for('.get_pouring_process'))
    return render_template('add_pouring_process.html', form=form)


@main.route('/get_pouring_process')
def get_pouring_process():
    pouring_processes = db.session.query(GlobalPouringProcess).all()
    return render_template('get_pouring_process.html', pouring_processes=pouring_processes, endopoints='.get_pouring_process')


@main.route('/edit_pouring_process/<int:id>', methods=['GET', 'POST'])
def edit_pouring_process(id):
    form = PouringProcessForm()
    pouring_process = db.session.query(GlobalPouringProcess).get_or_404(id)
    if form.validate_on_submit() and pouring_process is not None:
        pouring_process.pouring_time = form.pouring_time.data
        db.session.commit()
        return redirect(url_for('.get_pouring_process'))
    form.pouring_time.data = pouring_process.pouring_time
    return render_template('edit_pouring_process.html', form=form)


@main.route('/get_boiling', methods=['GET', 'POST'])
def get_boiling():
    boilings = db.session.query(Boiling).all()
    return render_template('get_boiling.html', boilings=boilings, endpoints='.get_boiling')


@main.route('/delete_boiling/<int:boiling_id>', methods=['DELETE'])
def delete_boiling(boiling_id):
    boiling_process = db.session.query(Boiling).get_or_404(boiling_id)
    if boiling_process:
        db.session.delete(boiling_process)
        db.session.commit()
    return redirect(url_for('.get_boiling'))


@main.route('/edit_boiling/<int:boiling_id>',  methods=['GET', 'POST'])
def edit_boiling(boiling_id):
    form = BoilingForm()
    with db.session.no_autoflush:
        boiling_process = db.session.query(Boiling).get_or_404(boiling_id)
        if form.validate_on_submit() and boiling_process is not None:
            boiling_process.percent = form.percent.data
            boiling_process.priority = form.priority.data
            boiling_process.is_lactose = form.is_lactose.data
            boiling_process.ferment = dict(form.ferment.choices).get(form.ferment.data)

            pouring_process = Pouring(
                pouring_time=form.pouring_time.data,
                soldification_time=form.soldification_time.data,
                cutting_time=form.cutting_time.data,
                pouring_off_time=form.pouring_off_time.data,
                extra_time=form.extra_time.data
            )
            boiling_process.pourings = pouring_process

            melting_process = Melting(
                serving_time=form.serving_time.data,
                melting_time=form.melting_time.data,
                speed=form.speed.data,
                first_cooling_time=form.first_cooling_time.data,
                second_cooling_time=form.second_cooling_time.data,
                salting_time=form.salting_time.data
            )
            boiling_process.meltings = melting_process

            db.session.commit()
            return redirect(url_for('.get_boiling'))
        for key, value in dict(form.ferment.choices).items():
            if value == boiling_process.ferment:
                form.ferment.default = key
                form.process()
        form.percent.data = boiling_process.percent
        form.priority.data = boiling_process.priority
        form.is_lactose.data = boiling_process.is_lactose


        if boiling_process.pourings is not None:
            form.pouring_time.data = boiling_process.pourings.pouring_time
            form.soldification_time.data = boiling_process.pourings.soldification_time
            form.cutting_time.data = boiling_process.pourings.cutting_time
            form.pouring_off_time.data = boiling_process.pourings.pouring_off_time
            form.extra_time.data = boiling_process.pourings.extra_time
        if boiling_process.meltings is not None:
            form.serving_time.data = boiling_process.meltings.serving_time
            form.melting_time.data = boiling_process.meltings.melting_time
            form.speed.data = boiling_process.meltings.speed
            form.first_cooling_time.data = boiling_process.meltings.first_cooling_time
            form.second_cooling_time.data = boiling_process.meltings.second_cooling_time
            form.salting_time.data = boiling_process.meltings.salting_time

        return render_template('edit_boiling.html', form=form)


@main.route('/add_boiling', methods=['GET', 'POST'])
def add_boilings():
    form = BoilingForm()
    if form.validate_on_submit():
        boiling = Boiling(
            percent=form.percent.data,
            priority=form.priority.data,
            is_lactose=form.is_lactose.data
        )
        pouring_process = Pouring(
            pouring_time=form.pouring_time.data,
            soldification_time=form.soldification_time.data,
            cutting_time=form.cutting_time.data,
            pouring_off_time=form.pouring_off_time.data,
            extra_time=form.extra_time.data
        )
        melting_process = Melting(
            serving_time=form.serving_time.data,
            melting_time=form.melting_time.data,
            speed=form.speed.data,
            first_cooling_time=form.first_cooling_time.data,
            second_cooling_time=form.second_cooling_time.data,
            salting_time=form.salting_time.data
        )
        boiling.pourings = pouring_process
        boiling.meltings = melting_process
        db.session.add(boiling)
        db.session.commit()
        return redirect(url_for('.get_boiling'))
    return render_template('add_boiling.html', form=form)


@main.route('/get_packings/<int:boiling_id>', methods=['GET', 'POST'])
def get_packings(boiling_id):
    pass


@main.route('/parse_request', methods=['GET', 'POST'])
def parse_request():
    form = RequestForm()
    result_list = []
    if request.method == 'POST' and form.validate_on_submit():
        date = form.date.data
        # create excel file for request

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
                request_weight = sum([x["Request"] for x in group_sku])
                result_list.append({
                    "GroupSKU": group_sku,
                    "BoilingId": group_sku[0]["SKU"].boiling_id,
                    "BoilingCount": request_weight / output_weight
                })

        build_plan(date, df_save, request_list=result_list)
        return render_template('parse_request.html', data=data, form=form, result_list=result_list)
    data = None
    result_list = None
    return render_template('parse_request.html', data=data, form=form, result_list=result_list)


@main.route('/process_request', methods=['GET', 'POST'])
def process_request():
    pass


@main.route('/get_lines', methods=['GET', 'POST'])
def get_lines():
    lines = db.session.query(Line).all()
    return jsonify([x.serialize() for x in lines])


@main.route('/get_packer', methods=['GET', 'POST'])
def get_packer():
    packers = db.session.query(Packer).all()
    return jsonify([x.serialize() for x in packers])


@main.route('/get_termizator', methods=['GET', 'POST'])
def get_termizator():
    termizator = db.session.query(Termizator).all()
    return jsonify([x.serialize() for x in termizator])


@main.route('/get_department', methods=['GET', 'POST'])
def get_department():
    departments = db.session.query(Departmenent).all()
    return jsonify([x.serialize() for x in departments])


