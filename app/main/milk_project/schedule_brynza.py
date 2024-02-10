from datetime import datetime, timedelta

import flask
import flask_login

from app.main import main
from app.main.milk_project.forms import BrynzaScheduleForm
from app.models import BatchNumber


@main.route("/brynza_schedule", methods=["GET", "POST"])
@flask_login.login_required
def brynza_schedule():
    form = BrynzaScheduleForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        date = form.date.data
        beg_time = form.beg_time.data
        brynza_kg = form.brynza_kg
        chanakh_kg = form.chanakh_kg

    form.date.data = datetime.today() + timedelta(days=1)
    form.batch_number.data = (
        BatchNumber.last_batch_number(
            date=datetime.today() + timedelta(days=1),
            department_name="Милкпроджект",
            group="brynza",
        )
        + 1
    )

    return flask.render_template("milk_project/schedule_brynza.html", form=form, filename=None)
