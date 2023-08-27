from datetime import datetime, timedelta

import flask
import flask_login

from app.main import main
from app.main.mascarpone.forms import UploadForm
from app.utils.files.utils import save_schedule


@main.route("/mascarpone_upload_schedule", methods=["GET", "POST"])
@flask_login.login_required
def mascarpone_upload_schedule():
    form = UploadForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        date = form.date.data
        file = flask.request.files["input_file"]
        filename_schedule = "{} {}.xlsx".format(date.strftime("%Y-%m-%d"), "Расписание маскарпоне")
        if file:
            save_schedule(file, filename_schedule, date.strftime("%Y-%m-%d"))

        return flask.render_template(
            "mascarpone/upload_schedule.html", form=form, filename=filename_schedule, date=date.strftime("%Y-%m-%d")
        )

    form.date.data = datetime.today() + timedelta(days=1)
    return flask.render_template("mascarpone/upload_schedule.html", form=form, filename=None, date=None)
