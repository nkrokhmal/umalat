from app.imports.runtime import *

from werkzeug.utils import redirect
import itertools
from app.main import main
from app.main.milk_project.forms import MilkProjectBoilingForm
from app.models import MilkProjectBoiling, MilkProjectSKU


@main.route("/milk_project/get_boiling", methods=["GET", "POST"])
@flask_login.login_required
def milk_project_get_boiling():
    boilings = db.session.query(MilkProjectBoiling).all()
    return flask.render_template(
        "milk_project/get_boiling.html",
        boilings=boilings,
        endpoints=".milk_project_get_boiling",
    )


@main.route(
    "/milk_project/edit_boiling/<int:boiling_id>",
    methods=["GET", "POST"],
)
@flask_login.login_required
def milk_project_edit_boiling(boiling_id):
    form = MilkProjectBoilingForm()
    boiling = db.session.query(MilkProjectBoiling).get_or_404(
        boiling_id
    )
    if form.validate_on_submit() and boiling is not None:
        boiling.output_coeff = form.output_coeff.data
        boiling.output_kg = form.output_kg.data

        db.session.commit()
        flask.flash("Параметры технологии успешно изменены", "success")
        return redirect(flask.url_for(".milk_project_get_boiling"))

    form.output_coeff.data = boiling.output_coeff
    form.output_kg.data = boiling.output_kg
    form.name.data = boiling.name

    return flask.render_template(
        "milk_project/edit_boiling.html",
        form=form,
        boiling_id=boiling.id,
    )
