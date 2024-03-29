from werkzeug.utils import redirect

from app.imports.runtime import *
from app.main import main
from app.models import MozzarellaBoilingTechnology
from app.utils.features.form_utils import *

from .forms import BoilingTechnologyForm


@main.route("/mozzarella/get_boiling_technology", methods=["GET", "POST"])
@flask_login.login_required
def get_boiling_technology():
    boiling_technologies = db.session.query(MozzarellaBoilingTechnology).all()
    return flask.render_template(
        "mozzarella/get_boiling_technology.html",
        boiling_technologies=boiling_technologies,
        endpoints=".get_boiling",
    )


@main.route(
    "/mozzarella/edit_boiling_technology/<int:boiling_technology_id>",
    methods=["GET", "POST"],
)
@flask_login.login_required
def edit_boiling_technology(boiling_technology_id):
    form = BoilingTechnologyForm()
    boiling_technology = db.session.query(MozzarellaBoilingTechnology).get_or_404(boiling_technology_id)
    if form.validate_on_submit() and boiling_technology is not None:
        boiling_technology.name = form.name.data
        boiling_technology.pouring_time = form.pouring_time.data
        boiling_technology.soldification_time = form.soldification_time.data
        boiling_technology.cutting_time = form.cutting_time.data
        boiling_technology.pouring_off_time = form.pouring_off_time.data
        boiling_technology.extra_time = form.extra_time.data

        db.session.commit()
        flask.flash("Параметры технологии варки успешно изменены", "success")
        return redirect(flask.url_for(".get_boiling_technology"))

    if boiling_technology.boiling.line is not None:
        form.line.default = default_form_value(form.line, boiling_technology.boiling.line.name)

    form.process()

    form.name.data = boiling_technology.name
    form.pouring_time.data = boiling_technology.pouring_time
    form.soldification_time.data = boiling_technology.soldification_time
    form.cutting_time.data = boiling_technology.cutting_time
    form.pouring_off_time.data = boiling_technology.pouring_off_time
    form.extra_time.data = boiling_technology.extra_time

    return flask.render_template(
        "mozzarella/edit_boiling_technology.html",
        form=form,
        boiling_technology_id=boiling_technology.id,
    )
