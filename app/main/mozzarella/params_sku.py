from werkzeug.utils import redirect

from app.imports.runtime import *
from app.main import main
from app.models import SKU, MozzarellaSKU
from app.utils.features.form_utils import *

from .forms import CopySKUForm, SKUForm


@main.route("/mozzarella/add_sku", methods=["POST", "GET"])
@flask_login.login_required
def mozzarella_add_sku():
    form = SKUForm()
    name = flask.request.args.get("name")
    if form.validate_on_submit():
        sku = MozzarellaSKU(
            name=form.name.data,
            brand_name=form.brand_name.data,
            weight_netto=form.weight_netto.data,
            shelf_life=form.shelf_life.data,
            packing_speed=form.packing_speed.data,
            collecting_speed=form.packing_speed.data,
            in_box=form.in_box.data,
            code=form.code.data,
        )
        sku = fill_mozzarella_sku_from_form(sku, form)
        db.session.add(sku)
        db.session.commit()
        flask.flash("SKU успешно добавлено", "success")
        return redirect(flask.url_for(".mozzarella_get_sku", page=1))
    if name:
        form.name.data = name
    return flask.render_template("mozzarella/add_sku.html", form=form)


@main.route("/mozzarella/get_sku/<int:page>", methods=["GET"])
@flask_login.login_required
def mozzarella_get_sku(page):
    db.session.remove()
    form = SKUForm()
    skus_count = db.session.query(MozzarellaSKU).count()

    pagination = (
        db.session.query(MozzarellaSKU)
        .order_by(MozzarellaSKU.name)
        .paginate(page=page, per_page=flask.current_app.config["SKU_PER_PAGE"], error_out=False)
    )
    return flask.render_template(
        "mozzarella/get_sku.html",
        form=form,
        pagination=pagination,
        page=page,
        skus_count=skus_count,
        per_page=flask.current_app.config["SKU_PER_PAGE"],
        endopoints=".get_sku",
    )


@main.route("/mozzarella/copy_sku/<int:sku_id>", methods=["GET", "POST"])
@flask_login.login_required
def mozzarella_copy_sku(sku_id):
    form = CopySKUForm()
    sku: MozzarellaSKU = db.session.query(MozzarellaSKU).get_or_404(sku_id)
    if form.validate_on_submit() and sku is not None:
        if form.name.data == sku.name:
            raise Exception("SKU с таким именем уже сущесвует в базе данных!")
        if form.code.data == sku.code:
            raise Exception("SKU с таким кодом уже существует в базе данных!")

        copy_sku = MozzarellaSKU(
            name=form.name.data,
            brand_name=form.brand_name.data,
            code=form.code.data,
            weight_netto=sku.weight_netto,
            shelf_life=sku.shelf_life,
            packing_speed=sku.packing_speed,
            collecting_speed=sku.packing_speed,
            in_box=sku.in_box,
            type=sku.type,
            group=sku.group,
            line=sku.line,
            form_factor=sku.form_factor,
            pack_type=sku.pack_type,
            made_from_boilings=sku.made_from_boilings,
            packers=sku.packers,
            production_by_request=sku.production_by_request,
            packing_by_request=sku.packing_by_request,
            melting_speed=sku.melting_speed,
        )
        db.session.add(copy_sku)
        db.session.commit()
        flask.flash("SKU успешно добавлено", "success")
        return redirect(flask.request.referrer or flask.url_for(".mozzarella_get_sku", page=1))
    form.name.data = sku.name
    form.brand_name.data = sku.brand_name
    form.code.data = sku.code
    return flask.render_template("mozzarella/copy_sku.html", form=form, sku_id=sku.id)


@main.route("/mozzarella/edit_sku/<int:sku_id>", methods=["GET", "POST"])
@flask_login.login_required
def mozzarella_edit_sku(sku_id):
    form = SKUForm()
    sku = db.session.query(MozzarellaSKU).get_or_404(sku_id)
    if form.validate_on_submit() and sku is not None:
        sku.name = form.name.data
        sku.brand_name = form.brand_name.data
        sku.weight_netto = form.weight_netto.data
        sku.shelf_life = form.shelf_life.data
        sku.packing_speed = form.packing_speed.data
        sku.melting_speed = form.melting_speed.data
        sku.in_box = form.in_box.data
        sku.code = form.code.data

        fill_mozzarella_sku_from_form(sku, form)

        db.session.commit()

        flask.flash("SKU успешно изменено", "success")
        return redirect(flask.request.referrer or flask.url_for(".mozzarella_get_sku", page=1))

    if len(sku.made_from_boilings) > 0:
        default_form_value(form.boiling, sku.made_from_boilings[0].to_str())

    if sku.line is not None:
        default_form_value(form.line, sku.line.name)

    if sku.group is not None:
        default_form_value(form.group, sku.group.name)

    if sku.pack_type is not None:
        default_form_value(form.pack_type, sku.pack_types.name)

    if sku.packers is not None:
        default_form_value(form.packer, sku.packers[0].name)

    if sku.form_factor is not None:
        default_form_value(form.form_factor, sku.form_factor.full_name)

    form.process()

    form.name.data = sku.name
    form.brand_name.data = sku.brand_name
    form.weight_netto.data = sku.weight_netto
    form.shelf_life.data = sku.shelf_life
    form.packing_speed.data = sku.packing_speed
    form.melting_speed.data = sku.melting_speed
    form.in_box.data = sku.in_box
    form.code.data = sku.code

    return flask.render_template("mozzarella/edit_sku.html", form=form, sku_id=sku_id)


@main.route("/mozzarella/delete_sku/<int:sku_id>", methods=["DELETE"])
@flask_login.login_required
def mozzarella_delete_sku(sku_id: int):
    sku = db.session.query(MozzarellaSKU).get_or_404(sku_id)
    logger.info(sku.name)
    if sku:
        db.session.delete(sku)
        db.session.commit()
        # flask.flash("SKU успешно удалено", "success")
    return redirect(flask.request.referrer or flask.url_for(".mozzarella_get_sku", page=1))
