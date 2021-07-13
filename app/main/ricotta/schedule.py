from app.main import main
from app.scheduler import *
from app.scheduler.ricotta import *
# from app.utils.ricotta.schedule_tasks import schedule_task_boilings, update_total_schedule_task
from app.utils.ricotta.schedule_tasks import RicottaScheduleTask
from app.utils.batches.batch import *
from app.utils.files.utils import save_schedule, save_schedule_dict
from .forms import ScheduleForm


@main.route("/ricotta_schedule", methods=["GET", "POST"])
@flask_login.login_required
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
        filename_schedule_pickle = f"{date.strftime('%Y-%m-%d')} Расписание рикотта.pickle"

        schedule_task = RicottaScheduleTask(
            df=boiling_plan_df,
            date=date,
            model=RicottaSKU,
            department="Рикоттный цех"
        )

        schedule_task.update_total_schedule_task()
        schedule_task.update_boiling_schedule_task(form.batch_number.data)

        schedule_wb = schedule_task.schedule_task_original(schedule_wb)
        # schedule_wb = schedule_task.schedule_task_boilings(schedule_wb, form.batch_number.data)

        save_schedule(schedule_wb, filename_schedule, date.strftime("%Y-%m-%d"))
        save_schedule_dict(schedule.to_dict(), filename_schedule_pickle, date.strftime("%Y-%m-%d"))

        return flask.render_template(
            "ricotta/schedule.html", form=form, filename=filename_schedule, date=date.strftime("%Y-%m-%d"),
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
