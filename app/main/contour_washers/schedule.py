from app.imports.runtime import *
from app.main import main
from .forms import ScheduleForm
from app.scheduler import run_consolidated, run_contour_cleanings
from app.main.errors import internal_error


@main.route("/contour_washers_schedule", methods=["GET", "POST"])
@flask_login.login_required
def contour_washers_schedule():
    form = ScheduleForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        date = form.date.data
        date_str = date.strftime("%Y-%m-%d")
        tank_4 = form.tank_4.data
        tank_5 = form.tank_5.data
        tank_8 = form.tank_8.data
        is_not_working_day = form.is_not_working_day.data

        try:
            path = DebugConfig.abs_path(
                "app/data/dynamic/{}/schedule_dict/".format(date_str)
            )

            if not os.path.exists(path):
                raise Exception(
                    "Не найдены утвержденные расписания для данной даты: {}".format(
                        date
                    )
                )

            run_contour_cleanings(
                path,
                output_path=path,
                prefix=date_str,
                input_tanks=(["4", tank_4], ["5", tank_5], ["8", tank_8]),
                is_tomorrow_day_off=is_not_working_day,
            )
            run_consolidated(
                path,
                output_path=path,
                prefix=date_str,
            )
        except Exception as e:
            return internal_error(e)

    form.date.data = datetime.today() + timedelta(days=1)
    return flask.render_template("contour_washers/schedule.html", form=form)
