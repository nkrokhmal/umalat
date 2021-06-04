import flask

from app.imports.runtime import *

from app.main.errors import internal_error
from app.main import main
from app.scheduler import *
from app.scheduler.ricotta import *
from app.utils.ricotta.schedule_tasks import schedule_task_boilings, update_total_schedule_task
from app.utils.batches.batch import *

from .forms import ScheduleForm


@main.route("/ricotta_schedule", methods=["GET", "POST"])
def ricotta_schedule():

    form = ScheduleForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        date = form.date.data
        beg_time = form.beg_time.data
        file = flask.request.files["input_file"]

        file_path = os.path.join(flask.current_app.config["UPLOAD_TMP_FOLDER"], file.filename)
        if file:
            file.save(file_path)
        wb = openpyxl.load_workbook(
            filename=os.path.join(
                flask.current_app.config["UPLOAD_TMP_FOLDER"], file.filename
            ),
            data_only=True,
        )
        boiling_plan_df = read_boiling_plan(wb)
        add_batch(
            date,
            "Рикоттный цех",
            form.batch_number.data,
            form.batch_number.data + int(boiling_plan_df["boiling_id"].max()) - 1,
        )
        schedule = make_schedule(boiling_plan_df, form.batch_number.data)
        frontend = wrap_frontend(schedule, date=date, start_time=beg_time)

        schedule_wb = draw_excel_frontend(frontend, STYLE, open_file=False, fn=None)
        filename_schedule = f"{date.strftime('%Y-%m-%d')} Расписание рикотта.xlsx"
        path_schedule = "{}/{}".format(flask.current_app.config["SCHEDULE_PLAN_FOLDER"], filename_schedule)

        update_total_schedule_task(date, boiling_plan_df)
        schedule_wb = schedule_task_boilings(
            schedule_wb, boiling_plan_df, date, form.batch_number.data
        )

        schedule_wb.save(path_schedule)
        return flask.render_template(
            "ricotta/schedule.html", form=form, filename=filename_schedule
        )

    form.date.data = datetime.today() + timedelta(days=1)
    form.batch_number.data = (
        BatchNumber.last_batch_number(
            datetime.today() + timedelta(days=1),
            "Рикоттный цех",
        )
        + 1
    )

    return flask.render_template("ricotta/schedule.html", form=form, filename=None)
