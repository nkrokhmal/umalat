from app.imports.runtime import *

from werkzeug.utils import redirect

from app.main import main
from app.globals import db
from app.models import RicottaSKU, RicottaLine
from app.enum import LineName
from app.utils.features.form_utils import *

from .forms import SKUForm, CopySKUForm


@main.route("/ricotta/add_sku", methods=["POST", "GET"])
@flask_login.login_required
def ricotta_add_sku():
    form = SKUForm()
    name = flask.request.args.get("name")
    if form.validate_on_submit():
        sku = RicottaSKU(
            name=form.name.data,
            code=form.code.data,
            brand_name=form.brand_name.data,
            weight_netto=form.weight_netto.data,
            shelf_life=form.shelf_life.data,
            packing_speed=form.packing_speed.data,
            collecting_speed=form.packing_speed.data,
            in_box=form.in_box.data,
            output_per_tank=form.output_per_tank.data,
        )
        sku = fill_ricotta_sku_from_form(sku, form)
        ricotta_line = (
            db.session.query(RicottaLine)
            .filter(RicottaLine.name == LineName.RICOTTA)
            .first()
        )
        sku.line = ricotta_line

        db.session.add(sku)
        db.session.commit()
        flask.flash("SKU успешно добавлено", "success")
        return redirect(flask.url_for(".ricotta_get_sku", page=1))
    if name:
        form.name.data = name
    return flask.render_template("ricotta/add_sku.html", form=form)


@main.route("/ricotta/copy_sku/<int:sku_id>", methods=["GET", "POST"])
@flask_login.login_required
def ricotta_copy_sku(sku_id):
    form = CopySKUForm()
    sku = db.session.query(RicottaSKU).get_or_404(sku_id)
    if form.validate_on_submit() and sku is not None:
        if form.name.data == sku.name:
            raise Exception("SKU с таким именем уже сущесвует в базе данных!")
        if form.code.data == sku.code:
            raise Exception("SKU с таким кодом уже существует в базе данных!")

        copy_sku = RicottaSKU(
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
            output_per_tank=sku.output_per_tank,
            form_factor=sku.form_factor,
            pack_type=sku.pack_type,
            made_from_boilings=sku.made_from_boilings,
            packers=sku.packers,
        )
        db.session.add(copy_sku)
        db.session.commit()
        flask.flash("SKU успешно добавлено", "success")
        return redirect(flask.url_for(".get_sku", page=1))
    form.name.data = sku.name
    form.brand_name.data = sku.brand_name
    form.code.data = sku.code
    return flask.render_template("ricotta/copy_sku.html", form=form, sku_id=sku.id)


@main.route("/ricotta/get_sku/<int:page>", methods=["GET"])
@flask_login.login_required
def ricotta_get_sku(page):
    form = SKUForm()
    db.session.remove()
    skus_count = db.session.query(RicottaSKU).count()

    pagination = (
        db.session.query(RicottaSKU)
        .order_by(RicottaSKU.name)
        .paginate(
            page, per_page=flask.current_app.config["SKU_PER_PAGE"], error_out=False
        )
    )
    return flask.render_template(
        "ricotta/get_sku.html",
        form=form,
        pagination=pagination,
        page=page,
        skus_count=skus_count,
        per_page=flask.current_app.config["SKU_PER_PAGE"],
        endopoints=".ricotta_get_sku",
    )


@main.route("/ricotta/edit_sku/<int:sku_id>", methods=["GET", "POST"])
@flask_login.login_required
def ricotta_edit_sku(sku_id):
    form = SKUForm()
    sku = db.session.query(RicottaSKU).get_or_404(sku_id)

    if form.validate_on_submit() and sku is not None:
        sku.name = form.name.data
        sku.code = form.code.data
        sku.brand_name = form.brand_name.data
        sku.weight_netto = form.weight_netto.data
        sku.shelf_life = form.shelf_life.data
        sku.output_per_tank = form.output_per_tank.data
        sku.packing_speed = form.packing_speed.data
        sku.in_box = form.in_box.data
        fill_ricotta_sku_from_form(sku, form)

        db.session.commit()

        flask.flash("SKU успешно изменено", "success")
        return redirect(flask.url_for(".ricotta_get_sku", page=1))

    if len(sku.made_from_boilings) > 0:
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
    form.output_per_tank.data = sku.output_per_tank

    return flask.render_template("ricotta/edit_sku.html", form=form, sku_id=sku_id)


@main.route("/ricotta/delete_sku/<int:sku_id>", methods=["DELETE"])
@flask_login.login_required
def ricotta_delete_sku(sku_id):
    sku = db.session.query(RicottaSKU).get_or_404(sku_id)
    if sku:
        db.session.delete(sku)
        db.session.commit()
        # flask.flash("SKU успешно удалено", "success")
    return redirect(flask.url_for(".ricotta_get_sku", page=1))
