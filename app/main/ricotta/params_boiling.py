from app.imports.runtime import *

from werkzeug.utils import redirect

from app.main import main
from app.models import RicottaBoiling

from app.main.ricotta.forms import BoilingForm


@main.route("/ricotta/get_boiling", methods=["GET", "POST"])
@flask_login.login_required
def ricotta_get_boiling():
    boilings = db.session.query(RicottaBoiling).all()
    return flask.render_template(
        "ricotta/get_boiling.html",
        boilings=boilings,
        endpoints=".ricotta_get_boiling",
    )


@main.route(
    "/ricotta/edit_boiling/<int:boiling_id>",
    methods=["GET", "POST"]
)
@flask_login.login_required
def ricotta_edit_boiling(boiling_id):
    form = BoilingForm()
    boiling = db.session.query(RicottaBoiling).get_or_404(
        boiling_id
    )
    if form.validate_on_submit() and boiling is not None:
        boiling.flavoring_agent = form.flavoring_agent.data
        boiling.percent = form.percent.data
        boiling.number_of_tanks = form.number_of_tanks.data

        db.session.commit()
        flask.flash("Параметры технологии успешно изменены", "success")
        return redirect(flask.url_for(".ricotta_get_boiling"))

    form.name.data = boiling.to_str()
    form.flavoring_agent.data = boiling.flavoring_agent
    form.percent.data = boiling.percent
    form.number_of_tanks.data = boiling.number_of_tanks

    return flask.render_template(
        "ricotta/edit_boiling.html",
        form=form,
        boiling_id=boiling.id,
    )
