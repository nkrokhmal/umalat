from app.imports.runtime import *

from app.main import main
from app.globals import db
from app.models import MascarponeSKU, MascarponeLine, Group
from app.enum import LineName
from app.utils.features.form_utils import *

from .forms import SKUMascarponeForm


@main.route("/mascarpone/add_sku_cream", methods=["POST", "GET"])
def mascarpone_add_sku_cream():
    form = SKUMascarponeForm()
    name = flask.request.args.get("name")
    if form.validate_on_submit():
        sku = MascarponeSKU(
            name=form.name.data,
            brand_name=form.brand_name.data,
            weight_netto=form.weight_netto.data,
            shelf_life=form.shelf_life.data,
            packing_speed=form.packing_speed.data,
            collecting_speed=form.packing_speed.data,
            in_box=form.in_box.data,
        )
        sku = fill_mascarpone_sku_from_form(sku, form)
        mascarpone_line = (
            db.session.query(MascarponeLine)
            .filter(MascarponeLine.name == LineName.MASCARPONE)
            .first()
        )
        sku.line = mascarpone_line

        db.session.add(sku)
        db.session.commit()
        flask.flash("SKU успешно добавлено", "success")
        return redirect(flask.url_for(".mascarpone_get_sku_cream", page=1))
    if name:
        form.name.data = name
    return flask.render_template("mascarpone/add_sku_cream.html", form=form)


@main.route("/mascarpone/get_sku_cream/<int:page>", methods=["GET"])
def mascarpone_get_sku_cream(page):
    flask.session.clear()
    form = SKUMascarponeForm()
    skus_count = db.session.query(MascarponeSKU).count()
    pagination = (
        db.session.query(MascarponeSKU)
        .join(Group)
        .filter(Group.name == "Сливки")
        .order_by(MascarponeSKU.name)
        .paginate(page, per_page=flask.current_app.config["SKU_PER_PAGE"], error_out=False)
    )
    return flask.render_template(
        "mascarpone/get_sku_cream.html",
        form=form,
        pagination=pagination,
        page=page,
        skus_count=skus_count,
        per_page=flask.current_app.config["SKU_PER_PAGE"],
        endopoints=".mascarpone_get_sku_cream",
    )


@main.route("/mascarpone/edit_sku_cream/<int:sku_id>", methods=["GET", "POST"])
def mascarpone_edit_sku_cream(sku_id):
    form = SKUMascarponeForm()
    sku = db.session.query(MascarponeSKU).get_or_404(sku_id)
    if form.validate_on_submit() and sku is not None:
        sku.name = form.name.data
        sku.brand_name = form.brand_name.data
        sku.weight_netto = form.weight_netto.data
        sku.shelf_life = form.shelf_life.data
        sku.packing_speed = form.packing_speed.data
        sku.in_box = form.in_box.data
        fill_mascarpone_sku_from_form(sku, form)

        db.session.commit()

        flask.flash("SKU успешно изменено", "success")
        return redirect(flask.url_for(".mascarpone_get_sku_cream", page=1))

    if len(sku.made_from_boilings) > 0:
        default_form_value(form.boiling, sku.made_from_boilings[0].to_str())

    if sku.group is not None:
        default_form_value(form.group, sku.group.name)

    form.process()

    form.name.data = sku.name
    form.brand_name.data = sku.brand_name
    form.weight_netto.data = sku.weight_netto
    form.shelf_life.data = sku.shelf_life
    form.packing_speed.data = sku.packing_speed
    form.in_box.data = sku.in_box

    return flask.render_template("mascarpone/edit_sku_cream.html", form=form, sku_id=sku_id)


@main.route("/mascarpone/delete_sku_cream/<int:sku_id>", methods=["DELETE"])
def mascarpone_delete_sku_cream(sku_id):
    sku = db.session.query(MascarponeSKU).get_or_404(sku_id)
    if sku:
        db.session.delete(sku)
        db.session.commit()
        flask.flash("SKU успешно удалено", "success")
    time.sleep(1.0)
    return redirect(flask.url_for(".mascarpone_get_sku_cream", page=1))
