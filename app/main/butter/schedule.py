import flask

from app.imports.runtime import *

from app.main import main
from app.scheduler.butter import *
from app.scheduler.butter.frontend.style import STYLE
from app.utils.batches.batch import *
from app.scheduler import draw_excel_frontend
from app.utils.files.utils import save_schedule, save_schedule_dict
from app.utils.butter.schedule_tasks import ButterScheduleTask
from .forms import ScheduleForm


@main.route("/butter_schedule", methods=["GET", "POST"])
@flask_login.login_required
def butter_schedule():

    form = ScheduleForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        date = form.date.data
        beg_time = form.beg_time.data
        file = flask.request.files["input_file"]

        file_path = os.path.join(
            flask.current_app.config["UPLOAD_TMP_FOLDER"], file.filename
        )
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
            "Масло цех",
            form.batch_number.data,
            form.batch_number.data + int(boiling_plan_df["boiling_id"].max()) - 1,
        )
        schedule = make_schedule(boiling_plan_df, start_time=beg_time)
        frontend = wrap_frontend(schedule, date=date)
        schedule_wb = draw_excel_frontend(frontend, STYLE, open_file=False, fn=None)

        filename_schedule = f"{date.strftime('%Y-%m-%d')} Расписание масло.xlsx"
        filename_schedule_pickle = (
            f"{date.strftime('%Y-%m-%d')} Расписание масло.pickle"
        )

        schedule_task = ButterScheduleTask(
            df=boiling_plan_df, date=date, model=ButterSKU, department="Маслоцех"
        )

        schedule_task.update_total_schedule_task()
        schedule_task.update_boiling_schedule_task(form.batch_number.data)

        # schedule_wb, _ = schedule_task.schedule_task_original(schedule_wb)
        schedule_wb, _ = schedule_task.schedule_task_boilings(
            schedule_wb, form.batch_number.data
        )

        save_schedule(schedule_wb, filename_schedule, date.strftime("%Y-%m-%d"))
        save_schedule_dict(
            schedule.to_dict(), filename_schedule_pickle, date.strftime("%Y-%m-%d")
        )
        os.remove(file_path)
        return flask.render_template(
            "butter/schedule.html",
            form=form,
            filename=filename_schedule,
            date=date.strftime("%Y-%m-%d"),
        )

    form.date.data = datetime.today() + timedelta(days=1)
    form.batch_number.data = (
        BatchNumber.last_batch_number(
            datetime.today() + timedelta(days=1),
            "Масло цех",
        )
        + 1
    )

    return flask.render_template("butter/schedule.html", form=form, filename=None)
