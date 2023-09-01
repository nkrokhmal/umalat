import flask
import flask_login

from app.globals import db
from app.main import main
from app.main.mascarpone.forms import MascarponeBoilingTechnologyForm
from app.models import MascarponeBoilingTechnology
from app.utils.flash_msgs import Action, boiling_technology_msg


@main.route("/mascarpone/get_boiling_technology", methods=["GET", "POST"])
@flask_login.login_required
def mascarpone_get_boiling_technology() -> str:
    technologies = db.session.query(MascarponeBoilingTechnology).all()
    return flask.render_template(
        "mascarpone/get_boiling_technology.html",
        boiling_technologies=technologies,
        endpoints=".mascarpone_get_boiling_technology",
    )


@main.route("/mascarpone/edit_boiling_technology/<int:boiling_technology_id>", methods=["GET", "POST"])
@flask_login.login_required
def mascarpone_edit_boiling_technology(boiling_technology_id: int) -> str | flask.Response:
    form = MascarponeBoilingTechnologyForm()
    bt: MascarponeBoilingTechnology = db.session.query(MascarponeBoilingTechnology).get_or_404(boiling_technology_id)

    if form.validate_on_submit():
        for attr in bt.dynamic_attributes:
            setattr(bt, attr, getattr(form, attr).data)

        db.session.commit()
        flask.flash(boiling_technology_msg(Action.ADD), "success")
        return flask.redirect(flask.url_for(".mascarpone_get_boiling_technology"))

    for attr in bt.dynamic_attributes + bt.readonly_attributes:
        if hasattr(form, attr):
            setattr(getattr(form, attr), "data", getattr(bt, attr))

    return flask.render_template(
        "mascarpone/edit_boiling_technology.html",
        form=form,
        boiling_technology_id=bt.id,
    )


__all__ = [
    "mascarpone_get_boiling_technology",
    "mascarpone_edit_boiling_technology",
]
