import flask

from app.imports.runtime import *
from app.main import main
from .forms import ScheduleForm
from app.scheduler import run_consolidated


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
    return flask.render_template(
        "departments_schedule/schedule.html",
        form=form,
    )