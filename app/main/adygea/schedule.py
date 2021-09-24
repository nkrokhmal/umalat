from app.main import main
from app.scheduler.adygea import *
from app.scheduler.adygea.frontend.style import STYLE
from app.utils.batches.batch import *
from app.scheduler import draw_excel_frontend
from app.utils.files.utils import save_schedule, save_schedule_dict, create_if_not_exists
from app.utils.adygea.schedule_tasks import AdygeaScheduleTask
from .forms import ScheduleForm


@main.route("/adygea_schedule", methods=["GET", "POST"])
@flask_login.login_required
def adygea_schedule():

    form = ScheduleForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        date = form.date.data
        beg_time = form.beg_time.data
        file = flask.request.files["input_file"]

        data_dir = os.path.join(
            flask.current_app.config["DYNAMIC_DIR"],
            date.strftime("%Y-%m-%d"),
            flask.current_app.config["BOILING_PLAN_FOLDER"])
        create_if_not_exists(data_dir)

        file_path = os.path.join(data_dir, file.filename)
        if file:
            file.save(file_path)
        wb = openpyxl.load_workbook(
            filename=os.path.join(
                data_dir, file.filename
            ),
            data_only=True,
        )

        boiling_plan_df = read_boiling_plan(wb)
        add_batch(
            date,
            "Адыгейский цех",
            form.batch_number.data,
            form.batch_number.data + int(boiling_plan_df["boiling_id"].max()) - 1,
        )
        schedule = make_schedule(boiling_plan_df, start_time=beg_time)
        frontend = wrap_frontend(schedule, date=date)
        schedule_template = openpyxl.load_workbook(
            filename=flask.current_app.config["TEMPLATE_SCHEDULE_PLAN_DEPARTMENT"],
            data_only=True,
        )
        schedule_wb = draw_excel_frontend(frontend, STYLE, open_file=False, fn=None, wb=schedule_template)

        filename_schedule = f"{date.strftime('%Y-%m-%d')} Расписание адыгейский.xlsx"
        filename_schedule_pickle = (
            f"{date.strftime('%Y-%m-%d')} Расписание адыгейский.pickle"
        )

        schedule_task = AdygeaScheduleTask(
            df=boiling_plan_df, date=date, model=AdygeaSKU, department="Адыгейский цех"
        )

        schedule_task.update_total_schedule_task()
        schedule_task.update_boiling_schedule_task(form.batch_number.data)

        schedule_wb, _ = schedule_task.schedule_task_original(schedule_wb)
        # schedule_wb, _ = schedule_task.schedule_task_boilings(
        #     schedule_wb, form.batch_number.data
        # )

        save_schedule(schedule_wb, filename_schedule, date.strftime("%Y-%m-%d"))
        save_schedule_dict(
            schedule.to_dict(), filename_schedule_pickle, date.strftime("%Y-%m-%d")
        )
        return flask.render_template(
            "adygea/schedule.html",
            form=form,
            filename=filename_schedule,
            date=date.strftime("%Y-%m-%d"),
        )

    form.date.data = datetime.today() + timedelta(days=1)
    form.batch_number.data = (
        BatchNumber.last_batch_number(
            datetime.today() + timedelta(days=1),
            "Адыгейский цех",
        )
        + 1
    )

    return flask.render_template("adygea/schedule.html", form=form, filename=None)
