import flask
import flask_login

from app.enum import LineName
from app.globals import db
from app.main import main
from app.main.mascarpone.forms import CopySKUForm, SKUMascarponeForm
from app.models.mascarpone import MascarponeLine, MascarponeSKU
from app.utils.features.form_utils import default_form_value, fill_mascarpone_sku_from_form
from app.utils.flash_msgs import sku_exception_msg, sku_successful_msg


@main.route("/mascarpone/add_sku_mascarpone", methods=["POST", "GET"])
@flask_login.login_required
def mascarpone_add_sku_mascarpone() -> flask.Response | str:
    form = SKUMascarponeForm()
    name = flask.request.args.get("name")
    if form.validate_on_submit():
        sku = MascarponeSKU(
            name=form.name.data,
            code=form.code.data,
            brand_name=form.brand_name.data,
            weight_netto=form.weight_netto.data,
            shelf_life=form.shelf_life.data,
            packing_speed=form.packing_speed.data,
            in_box=form.in_box.data,
        )
        sku = fill_mascarpone_sku_from_form(sku, form)
        mascarpone_line = db.session.query(MascarponeLine).filter(MascarponeLine.name == LineName.MASCARPONE).first()
        sku.line = mascarpone_line

        db.session.add(sku)
        db.session.commit()
        flask.flash(sku_successful_msg(), "success")
        return flask.redirect(flask.url_for(".mascarpone_get_sku", page=1))
    if name:
        form.name.data = name
    return flask.render_template("mascarpone/add_sku.html", form=form)


@main.route("/mascarpone/copy_sku/<int:sku_id>", methods=["GET", "POST"])
@flask_login.login_required
def mascarpone_copy_sku_mascarpone(sku_id: int) -> flask.Response | str:
    form = CopySKUForm()
    sku = db.session.query(MascarponeSKU).get_or_404(sku_id)
    if form.validate_on_submit():
        for attr in ("name", "code"):
            if getattr(form, attr).data == getattr(sku, attr):
                raise Exception(sku_exception_msg())

        copy_sku = MascarponeSKU(
            name=form.name.data,
            brand_name=form.brand_name.data,
            code=form.code.data,
            weight_netto=sku.weight_netto,
            shelf_life=sku.shelf_life,
            packing_speed=sku.packing_speed,
            collecting_speed=sku.packing_speed,
            in_box=sku.in_box,
            group=sku.group,
            type=sku.type,
            line=sku.line,
            form_factor=sku.form_factor,
            pack_type=sku.pack_type,
            made_from_boilings=sku.made_from_boilings,
            packers=sku.packers,
        )
        db.session.add(copy_sku)
        db.session.commit()
        flask.flash(sku_successful_msg(), "success")
        return flask.redirect(flask.url_for(".mascarpone_get_sku", page=1))

    form.name.data = sku.name
    form.brand_name.data = sku.brand_name
    form.code.data = sku.code
    return flask.render_template("mascarpone/copy_sku.html", form=form, sku_id=sku.id)


@main.route("/mascarpone/get_sku/<int:page>", methods=["GET"])
@flask_login.login_required
def mascarpone_get_sku(page) -> str:
    db.session.remove()
    form = SKUMascarponeForm()
    skus_count = db.session.query(MascarponeSKU).count()

    pagination = (
        db.session.query(MascarponeSKU)
        .order_by(MascarponeSKU.name)
        .paginate(page=page, per_page=flask.current_app.config["SKU_PER_PAGE"], error_out=False)
    )
    return flask.render_template(
        "mascarpone/get_sku.html",
        form=form,
        pagination=pagination,
        page=page,
        skus_count=skus_count,
        per_page=flask.current_app.config["SKU_PER_PAGE"],
        endopoints=".mascarpone_get_sku",
    )


@main.route("/mascarpone/edit_sku/<int:sku_id>", methods=["GET", "POST"])
@flask_login.login_required
def mascarpone_edit_sku(sku_id: int) -> flask.Response | str:
    form = SKUMascarponeForm()
    sku = db.session.query(MascarponeSKU).get_or_404(sku_id)
    if form.validate_on_submit():
        sku.name = form.name.data
        sku.code = form.code.data
        sku.brand_name = form.brand_name.data
        sku.weight_netto = form.weight_netto.data
        sku.shelf_life = form.shelf_life.data
        sku.packing_speed = form.packing_speed.data
        sku.in_box = form.in_box.data
        fill_mascarpone_sku_from_form(sku, form)

        db.session.commit()

        flask.flash(sku_successful_msg(action="change"), "success")
        return flask.redirect(flask.url_for(".mascarpone_get_sku", page=1))

    if sku.made_from_boilings:
        default_form_value(form.boiling, sku.made_from_boilings[0].to_str())

    if sku.group is not None:
        default_form_value(form.group, sku.group.name)

    form.process()
    form.name.data = sku.name
    form.code.data = sku.code
    form.brand_name.data = sku.brand_name
    form.weight_netto.data = sku.weight_netto
    form.shelf_life.data = sku.shelf_life
    form.packing_speed.data = sku.packing_speed
    form.in_box.data = sku.in_box

    return flask.render_template("mascarpone/edit_sku.html", form=form, sku_id=sku_id)


@main.route("/mascarpone/delete_sku/<int:sku_id>", methods=["DELETE"])
@flask_login.login_required
def mascarpone_delete_sku(sku_id: int) -> flask.Response:
    sku = db.session.query(MascarponeSKU).get_or_404(sku_id)

    db.session.delete(sku)
    db.session.commit()
    flask.flash(sku_successful_msg(action="delete"), "success")

    return flask.redirect(flask.url_for(".mascarpone_get_sku", page=1))
