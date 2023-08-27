import flask
import flask_login

from app.globals import db
from app.main import main
from app.main.mascarpone.forms import MascarponeBoilingForm
from app.models import MascarponeBoiling
from app.utils.flash_msgs import boiling_successful_msg


@main.route("/mascarpone/get_boiling", methods=["GET", "POST"])
@flask_login.login_required
def mascarpone_get_boiling() -> str:
    boilings = sorted(db.session.query(MascarponeBoiling).all(), key=lambda x: x.boiling_type)
    return flask.render_template(
        "mascarpone/get_boiling.html",
        boilings=boilings,
        endpoints=".mascarpone_get_boiling",
    )


@main.route("/mascarpone/edit_boiling/<int:boiling_id>", methods=["GET", "POST"])
@flask_login.login_required
def mascarpone_edit_boiling(boiling_id: int) -> str | flask.Response:
    form = MascarponeBoilingForm()
    boiling: MascarponeBoiling = db.session.query(MascarponeBoiling).get_or_404(boiling_id)

    if form.validate_on_submit():
        for attr in boiling.dynamic_attributes:
            setattr(boiling, attr, getattr(form, attr).data)

        db.session.commit()
        flask.flash(boiling_successful_msg(), "success")
        return flask.redirect(flask.url_for(".mascarpone_get_boiling"))

    for attr in boiling.dynamic_attributes + boiling.readonly_attributes:
        if hasattr(form, attr):
            setattr(getattr(form, attr), "data", getattr(boiling, attr))

    return flask.render_template(
        "mascarpone/edit_boiling.html",
        form=form,
        boiling_id=boiling.id,
    )


__all__ = [
    "mascarpone_get_boiling",
    "mascarpone_edit_boiling",
]
