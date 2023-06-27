from app.imports.runtime import *

from werkzeug.utils import redirect
import itertools
from app.main import main
from .forms import MascarponeBoilingTechnologyForm
from app.models import MascarponeBoilingTechnology, MascarponeSKU


@main.route("/mascarpone/get_boiling_technology_cream", methods=["GET", "POST"])
@flask_login.login_required
def mascarpone_get_boiling_technology_cream():
    skus = db.session.query(MascarponeSKU).all()
    skus_cream = [sku for sku in skus if sku.group.name == "Сливки"]
    boiling_technologies = [sku.made_from_boilings[0].boiling_technologies for sku in skus_cream]
    boiling_technologies = set(list(itertools.chain(*boiling_technologies)))
    return flask.render_template(
        "mascarpone/get_boiling_technology_cream.html",
        boiling_technologies=boiling_technologies,
        endpoints=".mascarpone_get_boiling_technology_cream",
    )


@main.route(
    "/mascarpone/edit_boiling_technology_cream/<int:boiling_technology_id>",
    methods=["GET", "POST"],
)
@flask_login.login_required
def mascarpone_edit_boiling_technology_cream(boiling_technology_id):
    form = MascarponeBoilingTechnologyForm()
    boiling_technology = db.session.query(MascarponeBoilingTechnology).get_or_404(
        boiling_technology_id
    )
    if form.validate_on_submit() and boiling_technology is not None:
        boiling_technology.name = form.name.data
        boiling_technology.pouring_time = form.pouring_time.data
        boiling_technology.heating_time = form.heating_time.data
        boiling_technology.adding_lactic_acid_time = form.adding_lactic_acid_time.data
        boiling_technology.pumping_off_time = form.pumping_off_time.data
        boiling_technology.ingredient_time = form.ingredient_time.data

        db.session.commit()
        flask.flash("Параметры технологии успешно изменены", "success")
        return redirect(flask.url_for(".mascarpone_get_boiling_technology_cream"))

    form.name.data = boiling_technology.name
    form.pouring_time.data = boiling_technology.pouring_time
    form.heating_time.data = boiling_technology.heating_time
    form.adding_lactic_acid_time.data = boiling_technology.adding_lactic_acid_time
    form.pumping_off_time.data = boiling_technology.pumping_off_time
    form.ingredient_time.data = boiling_technology.ingredient_time

    return flask.render_template(
        "mascarpone/edit_boiling_technology_cream.html",
        form=form,
        boiling_technology_id=boiling_technology.id,
    )
