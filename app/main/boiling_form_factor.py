from flask import url_for, render_template, flash, current_app, request
from werkzeug.utils import redirect
from . import main
from .. import db
from .forms import BoilingFormFactorForm
from ..models import SKU, BoilingFormFactor


@main.route('/add_boiling_form_factor', methods=['POST', 'GET'])
def add_boiling_form_factor():
    form = BoilingFormFactorForm()
    if form.validate_on_submit():
        bff = BoilingFormFactor(
            weight=form.weight.data,
            first_cooling_time=form.first_cooling_time.data,
            second_cooling_time=form.second_cooling_time.data,
            salting_time=form.salting_time.data
        )
        db.session.add(bff)
        try:
            db.session.commit()
            flash('Форм фактор плавления успешно добавлен!')
        except Exception as e:
            flash('Exception occurred in add_boiling_form_factor request. Error: {}.'.format(e), 'error')
            db.session.rollback()
        return redirect(url_for('.get_boiling_form_factor'))
    return render_template('add_boiling_form_factor.html', form=form)


@main.route('/get_boiling_form_factor', methods=['GET'])
def get_boiling_form_factor():
    page = request.args.get('page', 1, type=int)
    pagination = db.session.query(BoilingFormFactor) \
        .order_by(BoilingFormFactor.weight) \
        .paginate(
            page, per_page=current_app.config['SKU_PER_PAGE'],
            error_out=False
    )
    bffs = pagination.items
    return render_template('get_boiling_form_factor.html', bffs=bffs, paginations=pagination, endopoints='.get_boiling_form_factor')


@main.route('/edit_boiling_form_factor/<int:bff_id>', methods=['GET', 'POST'])
def edit_boiling_form_factor(bff_id):
    form = BoilingFormFactorForm()
    bff = db.session.query(BoilingFormFactor).get_or_404(bff_id)
    if form.validate_on_submit() and bff is not None:
        bff.weight = form.weight.data
        bff.first_cooling_time = form.first_cooling_time.data
        bff.seconds_cooling_time = form.second_cooling_time.data
        bff.salting_time = form.salting_time.data
        db.session.commit()
        flash('Форм фактор плавления успешно изменен!')
        return redirect(url_for('.get_boiling_form_factor'))

    form.weight.data = bff.weight
    form.first_cooling_time.data = bff.first_cooling_time
    form.second_cooling_time.data = bff.second_cooling_time
    form.salting_time = bff.salting_time
    return render_template('edit_boiling_form_factor.html', form=form)


@main.route('/delete_boiling_form_factor/<int:bff_id>', methods=['DELETE'])
def delete_boiling_form_factor(bff_id):
    bff = db.session.query(BoilingFormFactor).get_or_404(bff_id)
    if bff:
        db.session.delete(bff)
        db.session.commit()
        flash('Форм фактор плавления успешно удален!')
    return redirect(url_for('.get_boiling_form_factor'))
