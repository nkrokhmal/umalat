import flask
import flask_login

from app.globals import db
from app.main import main
from app.main.ricotta.forms import LineForm
from app.models import RicottaLine
from app.utils.flash_msgs import Action, line_msg


@main.route("/ricotta/get_line", methods=["GET", "POST"])
@flask_login.login_required
def ricotta_get_line():
    lines = db.session.query(RicottaLine).all()
    return flask.render_template("ricotta/get_line.html", lines=lines, endpoints=".ricotta_get_line")


@main.route("/ricotta/edit_line/<int:line_id>", methods=["GET", "POST"])
@flask_login.login_required
def ricotta_edit_line(line_id):
    form = LineForm()
    line = db.session.query(RicottaLine).get_or_404(line_id)
    if form.validate_on_submit() and line is not None:
        line.name = form.name.data
        line.input_kg = form.input_kg.data
        db.session.commit()
        flask.flash(line_msg(Action.ADD), "success")
        return flask.redirect(flask.url_for(".ricotta_get_line"))

    form.name.data = line.name
    form.input_kg.data = line.input_kg

    return flask.render_template("ricotta/edit_line.html", form=form, line_id=line.id)
