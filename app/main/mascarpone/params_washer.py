import flask
import flask_login

from app.enum import DepartmentName
from app.globals import db
from app.main import main
from app.main.mascarpone.forms import WasherForm
from app.models.basic import Department, Washer
from app.utils.flash_msgs import Action, washer_msg


@main.route("/mascarpone/get_washer", methods=["GET", "POST"])
@flask_login.login_required
def mascarpone_get_washer() -> str:
    washers: list[Washer] = (
        db.session.query(Washer).join(Washer.department).filter(Department.name == DepartmentName.MASCARPONE).all()
    )

    return flask.render_template(
        "mascarpone/get_washer.html",
        washers=washers,
        endpoints=".mascarpone_get_washer",
    )


@main.route(
    "/mascarpone/edit_washer/<int:washer_id>",
    methods=["GET", "POST"],
)
@flask_login.login_required
def mascarpone_edit_washer(washer_id: int):
    form = WasherForm()
    washer: Washer = db.session.query(Washer).get_or_404(washer_id)
    if form.validate_on_submit():
        washer.time = form.time.data
        db.session.commit()

        flask.flash(washer_msg(action=Action.EDIT), "success")
        return flask.redirect(flask.url_for(".mascarpone_get_washer"))

    form.name.data = washer.original_name
    form.time.data = washer.time

    return flask.render_template(
        "mascarpone/edit_washer.html",
        form=form,
        washer_id=washer.id,
    )


__all__ = [
    "mascarpone_get_washer",
    "mascarpone_edit_washer",
]
