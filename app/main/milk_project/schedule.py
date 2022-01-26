import flask

from app.imports.runtime import *

from app.main import main
from app.scheduler import run_adygea, run_milk_project, run_consolidated_old
from app.models import MilkProjectSKU, AdygeaSKU

from app.utils.batches.batch import *
from app.scheduler import draw_excel_frontend
from app.utils.files.utils import save_schedule, save_schedule_dict, create_if_not_exists
from app.utils.milk_project.schedule_tasks import MilkProjectScheduleTask
from app.utils.adygea.schedule_tasks import AdygeaScheduleTask
from app.scheduler.time import *

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

        milk_project_output = run_milk_project(wb,
                                               path=None,
                                               start_time=beg_time,
                                               first_batch_id=form.batch_number.data)
        prepare_start_time = beg_time
        if len(milk_project_output["boiling_plan_df"]) > 0:
            beg_time = cast_time(milk_project_output["schedule"].y[0] - 3) # 15 minutes before milk project ends # todo maybe: take from parameters
        else:
            # when no milk project - prepare start time is before beg_time
            prepare_start_time = cast_time(cast_t(prepare_start_time) - 12)
            # run milk project output again to match the new timing (will be empty, but with a timeline)
            milk_project_output = run_milk_project(wb, path=None, start_time=prepare_start_time)

        adygea_output = run_adygea(wb,
                                   path=None,
                                   start_time=beg_time,
                                   prepare_start_time=prepare_start_time,
                                   first_batch_id=form.batch_number.data)

        if (
            len(adygea_output["boiling_plan_df"]) > 0
            and len(milk_project_output["boiling_plan_df"]) > 0
        ):
            with code("Set preferred header time"):
                adygea_output["schedule"].props.update(
                    preferred_header_time=cast_time(
                        milk_project_output["schedule"].x[0]
                    ),
                )

        schedule_wb = run_consolidated_old(
            input_path=None,
            prefix=None,
            output_path=None,
            schedules={
                "milk_project": milk_project_output["schedule"],
                "adygea": adygea_output["schedule"],
            },
            date=date
        )

        if len(milk_project_output["boiling_plan_df"]) > 0:
            add_batch(
                date,
                "Милкпроджект",
                int(milk_project_output["boiling_plan_df"]['absolute_batch_id'].min()),
                int(milk_project_output["boiling_plan_df"]['absolute_batch_id'].max())
            )
        if len(adygea_output["boiling_plan_df"]) > 0:
            add_batch(
                date,
                "Адыгейский цех",
                int(adygea_output["boiling_plan_df"]['absolute_batch_id'].min()),
                int(adygea_output["boiling_plan_df"]['absolute_batch_id'].max())
            )

        filename_schedule = f"{date.strftime('%Y-%m-%d')} Расписание милкпроджект.xlsx"
        filename_schedule_pickle = (
            f"{date.strftime('%Y-%m-%d')} Расписание милкпроджект.pickle"
        )

        ScheduleTaskParams = namedtuple(
            "ScheduleTaskParams", "task,df,model,department"
        )

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
                department="Адыгейский цех",
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
            schedule_task.update_boiling_schedule_task()

            schedule_wb, cur_row = schedule_task.schedule_task_original(schedule_wb, cur_row=cur_row)
            # schedule_wb, cur_row = schedule_task.schedule_task_boilings(
            #     schedule_wb, form.batch_number.data, cur_row=cur_row
            # )

        save_schedule(schedule_wb, filename_schedule, date.strftime("%Y-%m-%d"))
        save_schedule_dict(
            milk_project_output["schedule"].to_dict(),
            filename_schedule_pickle,
            date.strftime("%Y-%m-%d"),
        )
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
