import flask

from app.imports.runtime import *
from app.main import main

from ...scheduler.run_consolidated import run_consolidated
from .forms import ScheduleForm


@main.route("/departments_schedule", methods=["GET", "POST"])
@flask_login.login_required
def departments_schedule():
    form = ScheduleForm(flask.request.form)
    if flask.request.method == "POST":
        date = form.date.data
        date_str = str(date.date())
        path = config.abs_path("app/data/dynamic/{}/approved/".format(date_str))
        run_consolidated(
            path,
            output_path=path,
            prefix=date_str,
        )
        filename = f"{date_str} Расписание общее.xlsx"
        return flask.render_template(
            "departments_schedule/schedule.html",
            date=date_str,
            filename=filename,
            form=form,
        )
    form.date.data = datetime.today() + timedelta(days=1)
    return flask.render_template(
        "departments_schedule/schedule.html",
        form=form,
    )
