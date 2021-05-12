from app.imports.runtime import *

from app.main import main
from app.models import MascarponeSKU, MascarponeLine, Group
from app.enum import *
from app.utils.features.form_utils import *

from .forms import SKUMascarponeForm


@main.route("/mascarpone/add_sku_mascarpone", methods=["POST", "GET"])
def mascarpone_add_sku_mascarpone():
    form = SKUMascarponeForm()
    name = request.args.get("name")
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
        flash("SKU успешно добавлено", "success")
        return redirect(url_for(".mascarpone_get_sku_mascarpone", page=1))
    if name:
        form.name.data = name
    return render_template("mascarpone/add_sku_mascarpone.html", form=form)


@main.route("/mascarpone/get_sku_mascarpone/<int:page>", methods=["GET"])
def mascarpone_get_sku_mascarpone(page):
    session.clear()
    form = SKUMascarponeForm()
    skus_count = db.session.query(MascarponeSKU).count()

    pagination = (
        db.session.query(MascarponeSKU)
        .join(Group)
        .filter(Group.name == "Маскарпоне")
        .order_by(MascarponeSKU.name)
        .paginate(page, per_page=current_app.configs["SKU_PER_PAGE"], error_out=False)
    )
    return render_template(
        "mascarpone/get_sku_mascarpone.html",
        form=form,
        pagination=pagination,
        page=page,
        skus_count=skus_count,
        per_page=current_app.configs["SKU_PER_PAGE"],
        endopoints=".mascarpone_get_sku_mascarpone",
    )


@main.route("/mascarpone/edit_sku_mascarpone/<int:sku_id>", methods=["GET", "POST"])
def mascarpone_edit_sku_mascarpone(sku_id):
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

        flash("SKU успешно изменено", "success")
        return redirect(url_for(".mascarpone_get_sku_mascarpone", page=1))

    if len(sku.made_from_boilings) > 0:
        print(sku.made_from_boilings[0].to_str())
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

    return render_template(
        "mascarpone/edit_sku_mascarpone.html", form=form, sku_id=sku_id
    )


@main.route("/mascarpone/delete_sku_mascarpone/<int:sku_id>", methods=["DELETE"])
def mascarpone_delete_sku_mascarpone(sku_id):
    sku = db.session.query(MascarponeSKU).get_or_404(sku_id)
    if sku:
        db.session.delete(sku)
        db.session.commit()
        flash("SKU успешно удалено", "success")
    time.sleep(1.0)
    return redirect(url_for(".mascarpone_get_sku_mascarpone", page=1))
