from app.imports.runtime import *

from werkzeug.utils import redirect

from app.main import main
from app.models import MascarponeSKU, MascarponeLine, Group
from app.enum import *
from app.utils.features.form_utils import *

from .forms import SKUMascarponeForm, CopySKUForm


@main.route("/mascarpone/add_sku_mascarpone", methods=["POST", "GET"])
@flask_login.login_required
def mascarpone_add_sku_mascarpone():
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
        return redirect(flask.url_for(".mascarpone_get_sku_mascarpone", page=1))
    if name:
        form.name.data = name
    return flask.render_template("mascarpone/add_sku_mascarpone.html", form=form)


@main.route("/mascarpone/copy_sku_mascarpone/<int:sku_id>", methods=["GET", "POST"])
@flask_login.login_required
def mascarpone_copy_sku_mascarpone(sku_id):
    form = CopySKUForm()
    sku = db.session.query(MascarponeSKU).get_or_404(sku_id)
    if form.validate_on_submit() and sku is not None:
        if form.name.data == sku.name:
            raise Exception("SKU с таким именем уже сущесвует в базе данных!")
        if form.code.data == sku.code:
            raise Exception("SKU с таким кодом уже существует в базе данных!")

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
        flask.flash("SKU успешно добавлено", "success")
        return redirect(flask.url_for(".mascarpone_get_sku_mascarpone", page=1))
    form.name.data = sku.name
    form.brand_name.data = sku.brand_name
    form.code.data = sku.code
    return flask.render_template("mascarpone/copy_sku_mascarpone.html", form=form, sku_id=sku.id)


@main.route("/mascarpone/get_sku_mascarpone/<int:page>", methods=["GET"])
@flask_login.login_required
def mascarpone_get_sku_mascarpone(page):
    db.session.remove()
    import time
    time.sleep(0.1)
    form = SKUMascarponeForm()
    skus_count = db.session.query(MascarponeSKU).count()

    pagination = (
        db.session.query(MascarponeSKU)
        .join(Group)
        .filter(Group.name == "Маскарпоне")
        .order_by(MascarponeSKU.name)
        .paginate(page, per_page=flask.current_app.config["SKU_PER_PAGE"], error_out=False)
    )
    return flask.render_template(
        "mascarpone/get_sku_mascarpone.html",
        form=form,
        pagination=pagination,
        page=page,
        skus_count=skus_count,
        per_page=flask.current_app.config["SKU_PER_PAGE"],
        endopoints=".mascarpone_get_sku_mascarpone",
    )


@main.route("/mascarpone/edit_sku_mascarpone/<int:sku_id>", methods=["GET", "POST"])
@flask_login.login_required
def mascarpone_edit_sku_mascarpone(sku_id):
    form = SKUMascarponeForm()
    sku = db.session.query(MascarponeSKU).get_or_404(sku_id)
    if form.validate_on_submit() and sku is not None:
        sku.name = form.name.data
        sku.code = form.code.data
        sku.brand_name = form.brand_name.data
        sku.weight_netto = form.weight_netto.data
        sku.shelf_life = form.shelf_life.data
        sku.packing_speed = form.packing_speed.data
        sku.in_box = form.in_box.data
        fill_mascarpone_sku_from_form(sku, form)

        db.session.commit()

        flask.flash("SKU успешно изменено", "success")
        return redirect(flask.url_for(".mascarpone_get_sku_mascarpone", page=1))

    if len(sku.made_from_boilings) > 0:
        print(sku.made_from_boilings[0].to_str())
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

    return flask.render_template(
        "mascarpone/edit_sku_mascarpone.html", form=form, sku_id=sku_id
    )


@main.route("/mascarpone/delete_sku_mascarpone/<int:sku_id>", methods=["DELETE"])
@flask_login.login_required
def mascarpone_delete_sku_mascarpone(sku_id):
    sku = db.session.query(MascarponeSKU).get_or_404(sku_id)
    if sku:
        db.session.delete(sku)
        db.session.commit()
        # flask.flash("SKU успешно удалено", "success")
    return redirect(flask.url_for(".mascarpone_get_sku_mascarpone", page=1))
