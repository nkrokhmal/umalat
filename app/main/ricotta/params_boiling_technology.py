from flask import url_for, render_template, flash
from werkzeug.utils import redirect
from .. import main
from ... import db
from .forms import BoilingTechnologyForm
from ...models import RicottaBoilingTechnology


@main.route("/ricotta/get_boiling_technology", methods=["GET", "POST"])
def ricotta_get_boiling_technology():
    boiling_technologies = db.session.query(RicottaBoilingTechnology).all()
    return render_template(
        "ricotta/get_boiling_technology.html",
        boiling_technologies=boiling_technologies,
        endpoints=".ricotta_get_boiling_technology",
    )


@main.route(
    "/ricotta/edit_boiling_technology/<int:boiling_technology_id>",
    methods=["GET", "POST"],
)
def ricotta_edit_boiling_technology(boiling_technology_id):
    form = BoilingTechnologyForm()
    boiling_technology = db.session.query(RicottaBoilingTechnology).get_or_404(
        boiling_technology_id
    )
    if form.validate_on_submit() and boiling_technology is not None:
        boiling_technology.name = form.name.data
        boiling_technology.heating_time = form.heating_time.data
        boiling_technology.delay_time = form.delay_time.data
        boiling_technology.protein_harvest_time = form.protein_harvest_time.data
        boiling_technology.abandon_time = form.abandon_time.data
        boiling_technology.pumping_out_time = form.pumping_out_time.data

        db.session.commit()
        flash("Варка успешно изменена!")
        return redirect(url_for(".ricotta_get_boiling_technology"))

    form.name.data = boiling_technology.name
    form.heating_time.data = boiling_technology.heating_time
    form.delay_time.data = boiling_technology.delay_time
    form.protein_harvest_time.data = boiling_technology.protein_harvest_time
    form.abandon_time.data = boiling_technology.abandon_time
    form.pumping_out_time.data = boiling_technology.pumping_out_time

    return render_template(
        "ricotta/edit_boiling_technology.html",
        form=form,
        boiling_technology_id=boiling_technology.id,
    )
