from app.imports.runtime import *
from app.main import main
from .forms import ScheduleForm


@main.route("/contour_washers_schedule", methods=["GET", "POST"])
@flask_login.login_required
def contour_washers_schedule():
    form = ScheduleForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        date = form.date.data
        tank_4 = form.tank_4.data
        tank_5 = form.tank_5.data
        tank_8 = form.tank_8.data
        is_not_working_day = form.is_not_working_day.data
        pass
    form.date.data = datetime.today() + timedelta(days=1)
    return flask.render_template(
        "contour_washers/schedule.html", form=form
    )