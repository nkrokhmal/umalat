from werkzeug.utils import redirect

from app.globals import db
from app.imports.runtime import *
from app.main import main
from app.models import ButterLine

from .forms import LineForm


@main.route("/butter/get_line", methods=["GET", "POST"])
@flask_login.login_required
def butter_get_line():
    lines = db.session.query(ButterLine).all()
    return flask.render_template("butter/get_line.html", lines=lines, endpoints=".butter_get_line")


@main.route("/butter/edit_line/<int:line_id>", methods=["GET", "POST"])
@flask_login.login_required
def butter_edit_line(line_id):
    form = LineForm()
    line = db.session.query(ButterLine).get_or_404(line_id)
    if form.validate_on_submit() and line is not None:
        line.name = form.name.data
        line.output_kg = form.output_kg.data
        line.preparing_time = form.preparing_time.data
        line.displacement_time = form.displacement_time.data
        line.cleaning_time = form.cleaning_time.data
        line.boiling_volume = form.boiling_volume.data
        db.session.commit()
        flask.flash("Параметры линии успешно изменены", "success")
        return redirect(flask.url_for(".butter_get_line"))

    form.name.data = line.name
    form.output_kg.data = line.output_kg
    form.preparing_time.data = line.preparing_time
    form.displacement_time.data = line.displacement_time
    form.cleaning_time.data = line.cleaning_time
    form.boiling_volume.data = line.boiling_volume

    return flask.render_template("butter/edit_line.html", form=form, line_id=line.id)
