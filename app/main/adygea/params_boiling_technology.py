import itertools

from werkzeug.utils import redirect

from app.imports.runtime import *
from app.main import main
from app.models import AdygeaBoilingTechnology, AdygeaSKU

from .forms import AdygeaBoilingTechnologyForm


@main.route("/adygea/get_boiling_technology", methods=["GET", "POST"])
@flask_login.login_required
def adygea_get_boiling_technology():
    skus = db.session.query(AdygeaSKU).all()
    boiling_technologies = [sku.made_from_boilings[0].boiling_technologies for sku in skus]
    boiling_technologies = set(list(itertools.chain(*boiling_technologies)))
    return flask.render_template(
        "adygea/get_boiling_technology.html",
        boiling_technologies=boiling_technologies,
        endpoints=".adygea_get_boiling_technology",
    )


@main.route(
    "/adygea/edit_boiling_technology/<int:boiling_technology_id>",
    methods=["GET", "POST"],
)
@flask_login.login_required
def adygea_edit_boiling_technology(boiling_technology_id):
    form = AdygeaBoilingTechnologyForm()
    boiling_technology = db.session.query(AdygeaBoilingTechnology).get_or_404(boiling_technology_id)
    if form.validate_on_submit() and boiling_technology is not None:
        boiling_technology.name = form.name.data
        boiling_technology.collecting_time = form.collecting_time.data
        boiling_technology.coagulation_time = form.coagulation_time.data
        boiling_technology.pouring_off_time = form.pouring_off_time.data

        db.session.commit()
        flask.flash("Параметры технологии успешно изменены", "success")
        return redirect(flask.url_for(".adygea_get_boiling_technology"))

    form.name.data = boiling_technology.name
    form.collecting_time.data = boiling_technology.collecting_time
    form.coagulation_time.data = boiling_technology.coagulation_time
    form.pouring_off_time.data = boiling_technology.pouring_off_time

    return flask.render_template(
        "adygea/edit_boiling_technology.html",
        form=form,
        boiling_technology_id=boiling_technology.id,
    )
