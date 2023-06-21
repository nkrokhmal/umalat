from app.imports.runtime import *

from werkzeug.utils import redirect
import itertools
from app.main import main
from app.main.adygea.forms import AdygeaBoilingForm
from app.models import AdygeaBoiling


@main.route("/adygea/get_boiling", methods=["GET", "POST"])
@flask_login.login_required
def adygea_get_boiling():
    boilings = db.session.query(AdygeaBoiling).all()
    return flask.render_template(
        "adygea/get_boiling.html",
        boilings=boilings,
        endpoints=".adygea_get_boiling",
    )


@main.route(
    "/adygea/edit_boiling/<int:boiling_id>",
    methods=["GET", "POST"],
)
@flask_login.login_required
def adygea_edit_boiling(boiling_id):
    form = AdygeaBoilingForm()
    boiling = db.session.query(AdygeaBoiling).get_or_404(
        boiling_id
    )
    if form.validate_on_submit() and boiling is not None:
        boiling.output_coeff = form.output_coeff.data
        boiling.output_kg = form.output_kg.data
        boiling.input_kg = form.input_kg.data

        db.session.commit()
        flask.flash("Параметры технологии успешно изменены", "success")
        return redirect(flask.url_for(".adygea_get_boiling"))

    form.output_coeff.data = boiling.output_coeff
    form.output_kg.data = boiling.output_kg
    form.input_kg.data = boiling.input_kg
    form.name.data = boiling.name

    return flask.render_template(
        "adygea/edit_boiling.html",
        form=form,
        boiling_id=boiling.id,
    )
