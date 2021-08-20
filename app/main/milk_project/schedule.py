import flask

from app.imports.runtime import *

from app.main import main
from app.scheduler import run_adygea, run_milk_project, run_consolidated
from app.models import MilkProjectSKU, AdygeaSKU

from app.utils.batches.batch import *
from app.scheduler import draw_excel_frontend
from app.utils.files.utils import save_schedule, save_schedule_dict
from app.utils.milk_project.schedule_tasks import MilkProjectScheduleTask
from app.utils.adygea.schedule_tasks import AdygeaScheduleTask
from .forms import ScheduleForm
from collections import namedtuple


@main.route("/milk_project_schedule", methods=["GET", "POST"])
@flask_login.login_required
def milk_project_schedule():

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

        milk_project_output = run_milk_project(wb, path=None, start_time=beg_time)
        adygea_output = run_adygea(wb, path=None, start_time=beg_time)

        schedule_wb = run_consolidated(
            input_path=None,
            prefix=None,
            output_path=None,
            schedules={
                "milk_project": milk_project_output["schedule"],
                "adygea": adygea_output["schedule"],
            },
        )

        add_batch(
            date,
            "Милкпроджект",
            form.batch_number.data,
            form.batch_number.data
            + int(milk_project_output["boiling_plan_df"]["boiling_id"].max())
            - 1,
        )
        add_batch(
            date,
            "Адыгейский цех",
            form.batch_number.data,
            form.batch_number.data
            + int(adygea_output["boiling_plan_df"]["boiling_id"].max())
            - 1,
        )

        filename_schedule = f"{date.strftime('%Y-%m-%d')} Расписание милкпроджект.xlsx"
        filename_schedule_pickle = (
            f"{date.strftime('%Y-%m-%d')} Расписание милкпроджект.pickle"
        )

        ScheduleTaskParams = namedtuple("ScheduleTaskParams", "task,df,model,department")

        schedule_task_params = [
            ScheduleTaskParams(
                task=MilkProjectScheduleTask,
                df=milk_project_output["boiling_plan_df"],
                model=MilkProjectSKU,
                department="Милкпроджект",
            ),
            ScheduleTaskParams(
                task=AdygeaScheduleTask,
                df=adygea_output["boiling_plan_df"],
                model=AdygeaSKU,
                department="Адыгейский",
            ),
        ]

        cur_row = 2
        for schedule_task_param in schedule_task_params:
            schedule_task = schedule_task_param.task(
                df=schedule_task_param.df,
                date=date,
                model=schedule_task_param.model,
                department=schedule_task_param.department,
            )

            schedule_task.update_total_schedule_task()
            schedule_task.update_boiling_schedule_task(form.batch_number.data)

            # schedule_wb = schedule_task.schedule_task_original(schedule_wb)
            schedule_wb, cur_row = schedule_task.schedule_task_boilings(
                schedule_wb, form.batch_number.data, cur_row=cur_row
            )

        save_schedule(schedule_wb, filename_schedule, date.strftime("%Y-%m-%d"))
        save_schedule_dict(
            milk_project_output["schedule"].to_dict(),
            filename_schedule_pickle,
            date.strftime("%Y-%m-%d"),
        )
        os.remove(file_path)
        return flask.render_template(
            "milk_project/schedule.html",
            form=form,
            filename=filename_schedule,
            date=date.strftime("%Y-%m-%d"),
        )

    form.date.data = datetime.today() + timedelta(days=1)
    form.batch_number.data = (
        BatchNumber.last_batch_number(
            datetime.today() + timedelta(days=1),
            "Милкпроджект",
        )
        + 1
    )

    return flask.render_template("milk_project/schedule.html", form=form, filename=None)
