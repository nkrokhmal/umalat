from flask import session, url_for, render_template, flash, request, make_response, current_app, request
from werkzeug.utils import redirect
from . import main
from .. import db
from .forms import BoilingForm
from ..models_new import Boiling, BoilingTechnology
from ..utils.form import *


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
        flash('Варка успешно удалена')
    return redirect(url_for('.get_boiling'))


@main.route('/edit_boiling/<int:boiling_id>',  methods=['GET', 'POST'])
def edit_boiling(boiling_id):
    form = BoilingForm()
    with db.session.no_autoflush:
        boiling = db.session.query(Boiling).get_or_404(boiling_id)
        if form.validate_on_submit() and boiling is not None:
            boiling.percent = form.percent.data
            boiling.is_lactose = form.is_lactose.data
            boiling.ferment = get_choice_data(form.ferment)

            boiling_technology = db.session.query(BoilingTechnology) \
                .filter_by(BoilingTechnology.pouring_time == form.pouring_time.data) \
                .filter_by(BoilingTechnology.soldification_time == form.soldification_time.data) \
                .filter_by(BoilingTechnology.cutting_time == form.cutting_time.data) \
                .filter_by(BoilingTechnology.pouring_off_time == form.pouring_off_time.data) \
                .filter_by(BoilingTechnology.extra_time == form.extra_time.data) \
                .first()

            if boiling_technology is None:
                boiling_technology = BoilingTechnology(
                    pouring_time=form.pouring_time.data,
                    soldification_time=form.soldification_time.data,
                    cutting_time=form.cutting_time.data,
                    pouring_off_time=form.pouring_off_time.data,
                    extra_time=form.extra_time.data
                )
            boiling.boiling_technology = boiling_technology

            if form.line.data != -1:
                boiling.line = [x for x in form.lines if x.name == get_choice_data(form.line)][0]

            db.session.commit()
            flash('Варка успешно изменена!')
            return redirect(url_for('.get_boiling'))

        if boiling.ferment is not None:
            form.ferment.default = default_form_value(boiling.ferment)

        if boiling.line is not None:
            form.line.default = default_form_value(boiling.line.name)

        form.process()

        form.percent.data = boiling.percent
        form.is_lactose.data = boiling.is_lactose

        if boiling.boiling_technology is not None:
            form.pouring_time.data = boiling.boiling_technology.pouring_time
            form.soldification_time.data = boiling.boiling_technology.soldification_time
            form.cutting_time.data = boiling.boiling_technology.cutting_time
            form.pouring_off_time.data = boiling.boiling_technology.pouring_off_time
            form.extra_time.data = boiling.boiling_technology.extra_time
        return render_template('edit_boiling.html', form=form)


@main.route('/add_boiling', methods=['GET', 'POST'])
def add_boilings():
    form = BoilingForm()
    if form.validate_on_submit():
        boiling = Boiling(
            percent=form.percent.data,
            is_lactose=form.is_lactose.data,
            ferment=get_choice_data(form.ferment)
        )
        boiling_technology = db.session.query(BoilingTechnology)\
            .filter_by(BoilingTechnology.pouring_time == form.pouring_time.data)\
            .filter_by(BoilingTechnology.soldification_time == form.soldification_time.data)\
            .filter_by(BoilingTechnology.cutting_time == form.cutting_time.data)\
            .filter_by(BoilingTechnology.pouring_off_time == form.pouring_off_time.data)\
            .filter_by(BoilingTechnology.extra_time == form.extra_time.data)\
            .first()

        if boiling_technology is None:
            boiling_technology = BoilingTechnology(
                pouring_time=form.pouring_time.data,
                soldification_time=form.soldification_time.data,
                cutting_time=form.cutting_time.data,
                pouring_off_time=form.pouring_off_time.data,
                extra_time=form.extra_time.data
            )
        boiling.boiling_technology = boiling_technology

        if form.line.data != -1:
            boiling.line = [x for x in form.lines if x.name == get_choice_data(form.line)][0]

        db.session.add(boiling)
        db.session.commit()
        flash('Варка успешно добавлена')
        return redirect(url_for('.get_boiling'))
    return render_template('add_boiling.html', form=form)