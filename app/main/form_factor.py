from flask import url_for, render_template, flash, current_app, request
from werkzeug.utils import redirect
from . import main
from .errors import internal_error
from .. import db
from ..utils.form import *
from .forms import FormFactorForm
from ..models_new import CoolingTechnology, FormFactor
from sqlalchemy import or_


@main.route('/add_form_factor', methods=['POST', 'GET'])
def add_form_factor():
    try:
        form = FormFactorForm()
        if form.validate_on_submit():
            form_factor = FormFactor(
                relative_weight=form.relative_weight.data)

            if form.group.data != -1:
                form_factor.group = [x for x in form.groups if x.name == get_choice_data(form.group)]

            cooling_technology = db.session.query(CoolingTechnology)\
                .filter_by(or_(form.first_cooling_time.data is None, CoolingTechnology.first_cooling_time == form.first_cooling_time.data))\
                .filter_by(or_(form.second_cooling_time.data is None, CoolingTechnology.second_cooling_time == form.second_cooling_time.data)) \
                .filter_by(or_(form.salting_time.data is None, CoolingTechnology.salting_time == form.ssalting_time.data)) \
                .first()
            if cooling_technology is None:
                cooling_technology = CoolingTechnology(
                    first_cooling_time=form.first_cooling_time.data,
                    second_cooling_time=form.second_cooling_time.data,
                    salting_time=form.salting_time.data
                )
                db.session.add(cooling_technology)
            form_factor.default_cooling_technology = cooling_technology
            db.session.add(form_factor)
            try:
                db.session.commit()
                flash('Форм фактор плавления успешно добавлен!')
            except Exception as e:
                flash('Exception occurred in add_boiling_form_factor request. Error: {}.'.format(e), 'error')
                db.session.rollback()
            return redirect(url_for('.get_form_factor'))
        return render_template('add_form_factor.html', form=form)
    except Exception as e:
        return internal_error(e)


@main.route('/get_form_factor', methods=['GET'])
def get_form_factor():
    try:
        page = request.args.get('page', 1, type=int)
        pagination = db.session.query(FormFactor) \
            .order_by(FormFactor.relative_weight) \
            .paginate(
                page, per_page=current_app.config['SKU_PER_PAGE'],
                error_out=False
        )
        form_factors = pagination.items
        return render_template('get_form_factor.html', form_factors=form_factors,
                               paginations=pagination, endopoints='.get_form_factor')
    except Exception as e:
        return internal_error(e)


@main.route('/edit_form_factor/<int:ff_id>', methods=['GET', 'POST'])
def edit_form_factor(ff_id):
    try:
        form = FormFactorForm()
        form_factor = db.session.query(FormFactor).get_or_404(ff_id)
        if form.validate_on_submit() and form_factor is not None:
            form_factor.weight = form.relative_weight.data
            if form.group.data != -1:
                form_factor.group = [x for x in form.groups if x.name == get_choice_data(form.group)]

            cooling_technology = db.session.query(CoolingTechnology) \
                .filter_by(or_(form.first_cooling_time.data is None,
                               CoolingTechnology.first_cooling_time == form.first_cooling_time.data)) \
                .filter_by(or_(form.second_cooling_time.data is None,
                               CoolingTechnology.second_cooling_time == form.second_cooling_time.data)) \
                .filter_by(or_(form.salting_time.data is None, CoolingTechnology.salting_time == form.ssalting_time.data)) \
                .first()
            if cooling_technology is None:
                cooling_technology = CoolingTechnology(
                    first_cooling_time=form.first_cooling_time.data,
                    second_cooling_time=form.second_cooling_time.data,
                    salting_time=form.salting_time.data
                )
                db.session.add(cooling_technology)
            form_factor.default_cooling_technology = cooling_technology
            db.session.commit()
            flash('Форм фактор успешно изменен!')
            return redirect(url_for('.get_form_factor'))

        if form_factor.group is not None:
            form.group.default = default_form_value(form_factor.group.name)

        form.process()

        form.relative_weight.data = form_factor.relative_weight
        form.first_cooling_time.data = form_factor.default_cooling_technology.first_cooling_time
        form.second_cooling_time.data = form_factor.default_cooling_technology.second_cooling_time
        form.salting_time = form_factor.default_cooling_technology.salting_time
        return render_template('edit_boiling_form_factor.html', form=form)
    except Exception as e:
        return internal_error(e)


@main.route('/delete_form_factor/<int:ff_id>', methods=['DELETE'])
def delete_form_factor(ff_id):
    try:
        bff = db.session.query(FormFactor).get_or_404(ff_id)
        if bff:
            db.session.delete(bff)
            db.session.commit()
            flash('Форм фактор плавления успешно удален!')
        return redirect(url_for('.get_boiling_form_factor'))
    except Exception as e:
        return internal_error(e)
