from flask import url_for, render_template, flash, current_app, request
from werkzeug.utils import redirect
from .. import main
from ... import db
from ..forms import SKUForm
from ...models import MozzarellaSKU
from app.utils.features.form_utils import *


@main.route('/mozzarella/add_sku', methods=['POST', 'GET'])
def add_sku():
    form = SKUForm()
    name = request.args.get('name')
    if form.validate_on_submit():
        sku = MozzarellaSKU(
            name=form.name.data,
            brand_name=form.brand_name.data,
            weight_netto=form.weight_netto.data,
            shelf_life=form.shelf_life.data,
            packing_speed=form.packing_speed.data,
            collecting_speed=form.packing_speed.data,
        )
        sku = fill_sku_from_form(sku, form)
        db.session.add(sku)
        db.session.commit()
        return redirect(url_for('.get_sku'))
    if name:
        form.name.data = name
    return render_template('mozzarella/add_sku.html', form=form)


@main.route('/mozzarella/get_sku', methods=['GET'])
def get_sku():
    form = SKUForm()
    page = request.args.get('page', 1, type=int)
    pagination = db.session.query(MozzarellaSKU) \
        .order_by(MozzarellaSKU.name) \
        .paginate(
        page, per_page=current_app.config['SKU_PER_PAGE'],
        error_out=False
    )
    skus = pagination.items
    return render_template('mozzarella/get_sku.html', form=form, skus=skus, paginations=pagination, endopoints='.get_sku')


@main.route('/edit_sku/<int:sku_id>', methods=['GET', 'POST'])
def edit_sku(sku_id):
    form = SKUForm()
    sku = db.session.query(SKU).get_or_404(sku_id)
    if form.validate_on_submit() and sku is not None:
        sku.name = form.name.data
        sku.brand_name = form.brand_name.data
        sku.weight_netto = form.weight_netto.data
        sku.shelf_life = form.shelf_life.data
        sku.packing_speed = form.packing_speed.data
        sku = fill_sku_from_form(sku, form)

        db.session.commit()
        flash('SKU успешно изменено')
        return redirect(url_for('.get_sku'))

    if len(sku.made_from_boilings) > 0:
        default_form_value(form.boiling, sku.made_from_boilings[0].to_str())

    if sku.line is not None:
        default_form_value(form.line, sku.line.name)

    if sku.group is not None:
        default_form_value(form.group, sku.group.name)

    if sku.pack_type is not None:
        default_form_value(form.pack_type, sku.pack_types.name)

    if sku.packer is not None:
        default_form_value(form.packer, sku.packer.name)

    if sku.form_factor is not None:
        default_form_value(form.form_factor, sku.form_factor.full_name)

    form.process()

    form.name.data = sku.name
    form.brand_name.data = sku.brand_name
    form.weight_netto.data = sku.weight_netto
    form.shelf_life.data = sku.shelf_life
    form.packing_speed.data = sku.packing_speed

    return render_template('edit_sku.html', form=form)


@main.route('/delete_sku/<int:sku_id>', methods=['DELETE'])
def delete_sku(sku_id):
    sku = db.session.query(SKU).get_or_404(sku_id)
    if sku:
        for boiling in sku.made_from_boilings:
            sku.made_from_boilings.remove(boiling)
        db.session.commit()
        db.session.delete(sku)
        db.session.commit()
        flash('SKU успешно удалено')
    return redirect(url_for('.get_sku'))
