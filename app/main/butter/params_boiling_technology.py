import itertools

from werkzeug.utils import redirect

from app.imports.runtime import *
from app.main import main
from app.models import ButterBoilingTechnology, ButterSKU

from .forms import ButterBoilingTechnologyForm


@main.route("/butter/get_boiling_technology", methods=["GET", "POST"])
@flask_login.login_required
def butter_get_boiling_technology():
    skus = db.session.query(ButterSKU).all()
    boiling_technologies = [sku.made_from_boilings[0].boiling_technologies for sku in skus]
    boiling_technologies = set(list(itertools.chain(*boiling_technologies)))
    return flask.render_template(
        "butter/get_boiling_technology.html",
        boiling_technologies=boiling_technologies,
        endpoints=".butter_get_boiling_technology",
    )


@main.route(
    "/butter/edit_boiling_technology/<int:boiling_technology_id>",
    methods=["GET", "POST"],
)
@flask_login.login_required
def butter_edit_boiling_technology(boiling_technology_id):
    form = ButterBoilingTechnologyForm()
    boiling_technology = db.session.query(ButterBoilingTechnology).get_or_404(boiling_technology_id)
    if form.validate_on_submit() and boiling_technology is not None:
        boiling_technology.name = form.name.data
        boiling_technology.separator_runaway_time = form.separator_runaway_time.data
        boiling_technology.pasteurization_time = form.pasteurization_time.data
        boiling_technology.increasing_temperature_time = form.increasing_temperature_time.data

        db.session.commit()
        flask.flash("Параметры технологии успешно изменены", "success")
        return redirect(flask.url_for(".butter_get_boiling_technology"))

    form.name.data = boiling_technology.name
    form.separator_runaway_time.data = boiling_technology.separator_runaway_time
    form.pasteurization_time.data = boiling_technology.pasteurization_time
    form.increasing_temperature_time.data = boiling_technology.increasing_temperature_time

    return flask.render_template(
        "butter/edit_boiling_technology.html",
        form=form,
        boiling_technology_id=boiling_technology.id,
    )
