from flask import url_for, render_template, flash
from werkzeug.utils import redirect
from .. import main
from ... import db
from .forms import MascarponeBoilingTechnologyForm
from ...models import MascarponeBoilingTechnology


@main.route("/mascarpone/get_boiling_technology_mascarpone", methods=["GET", "POST"])
def mascarpone_get_boiling_technology_mascarpone():
    boiling_technologies = db.session.query(MascarponeBoilingTechnology).all()
    return render_template(
        "mascarpone/get_boiling_technology_mascarpone.html",
        boiling_technologies=boiling_technologies,
        endpoints=".mascarpone_get_boiling_technology_mascarpone",
    )


@main.route(
    "/mascarpone/edit_boiling_technology_mascarpone/<int:boiling_technology_id>",
    methods=["GET", "POST"],
)
def mascarpone_edit_boiling_technology_mascarpone(boiling_technology_id):
    form = MascarponeBoilingTechnologyForm()
    boiling_technology = db.session.query(MascarponeBoilingTechnology).get_or_404(
        boiling_technology_id
    )
    if form.validate_on_submit() and boiling_technology is not None:
        boiling_technology.name = form.name.data
        boiling_technology.pouring_time = form.heating_time.data
        boiling_technology.heating_time = form.delay_time.data
        boiling_technology.adding_lactic_acid_time = form.protein_harvest_time.data
        boiling_technology.separation_time = form.abandon_time.data
        boiling_technology.fermentator_name = form.fermentator_name.data

        db.session.commit()
        flash("Параметры технологии успешно изменены", "success")
        return redirect(url_for(".mascarpone_get_boiling_technology_mascarpone"))

    form.name.data = boiling_technology.name
    form.heating_time.data = boiling_technology.heating_time
    form.delay_time.data = boiling_technology.delay_time
    form.protein_harvest_time.data = boiling_technology.protein_harvest_time
    form.abandon_time.data = boiling_technology.abandon_time
    form.pumping_out_time.data = boiling_technology.pumping_out_time

    return render_template(
        "mascarpone/edit_boiling_technology_mascarpone.html",
        form=form,
        boiling_technology_id=boiling_technology.id,
    )
