import flask

from app.imports.runtime import *
from app.main import main
from app.main.adygea.update_task_and_batches import update_task_and_batches as update_task_and_batches_adygea
from app.main.milk_project.update_task_and_batches import (
    update_task_and_batches as update_task_and_batches_milk_project,
)
from app.main.time_validator import *
from app.models import AdygeaSKU, MilkProjectSKU
from app.scheduler import draw_excel_frontend, run_adygea, run_consolidated_old, run_milk_project
from app.scheduler.frontend import fill_grid
from app.scheduler.time import *
from app.utils.adygea.schedule_tasks import AdygeaScheduleTask
from app.utils.batches.batch import *
from app.utils.files.utils import create_if_not_exists, save_schedule, save_schedule_dict
from app.utils.milk_project.schedule_tasks import MilkProjectScheduleTask

from .forms import ScheduleForm


@main.route("/milk_project_schedule", methods=["GET", "POST"])
@flask_login.login_required
def milk_project_schedule():
    form = ScheduleForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        date = form.date.data
        beg_time = form.beg_time.data

        # validate time
        time_validator(form, form.beg_time)

        file = flask.request.files["input_file"]

        data_dir = os.path.join(
            flask.current_app.config["DYNAMIC_DIR"],
            date.strftime("%Y-%m-%d"),
            flask.current_app.config["BOILING_PLAN_FOLDER"],
        )
        create_if_not_exists(data_dir)

        file_path = os.path.join(data_dir, file.filename)
        if file:
            file.save(file_path)
        wb = openpyxl.load_workbook(
            filename=os.path.join(data_dir, file.filename),
            data_only=True,
        )
        first_batch_ids = {"milk_project": form.batch_number.data}
        milk_project_output = run_milk_project(wb, path=None, start_time=beg_time)
        prepare_start_time = beg_time
        if len(milk_project_output["boiling_plan_df"]) > 0:
            beg_time = cast_time(
                milk_project_output["schedule"].y[0] - 3
            )  # 15 minutes before milk project ends # todo maybe: take from parameters
        else:
            # when no milk project - prepare start time is before beg_time
            prepare_start_time = cast_time(cast_t(prepare_start_time) - 12)
            # run milk project output again to match the new timing (will be empty, but with a timeline)
            milk_project_output = run_milk_project(wb, path=None, start_time=prepare_start_time)

        adygea_output = run_adygea(wb, path=None, start_time=beg_time, prepare_start_time=prepare_start_time)

        if len(adygea_output["boiling_plan_df"]) > 0 and len(milk_project_output["boiling_plan_df"]) > 0:
            with code("Set preferred header time"):
                adygea_output["schedule"].props.update(
                    preferred_header_time=cast_time(milk_project_output["schedule"].x[0]),
                )

        schedule_wb = run_consolidated_old(
            input_path=None,
            prefix=None,
            output_path=None,
            schedules={
                "milk_project": milk_project_output["schedule"],
                "adygea": adygea_output["schedule"],
            },
            date=date,
            wb=wb,
        )
        utils.write_metadata(schedule_wb, json.dumps({"first_batch_ids": first_batch_ids, "date": str(date)}))

        schedule_tasks = [
            update_task_and_batches_milk_project(schedule_wb),
            update_task_and_batches_adygea(schedule_wb),
        ]

        cur_row = 2
        for schedule_task in schedule_tasks:
            schedule_wb, cur_row = schedule_task.schedule_task_original(schedule_wb, cur_row=cur_row)
            # schedule_wb, cur_row = schedule_task.schedule_task_boilings(
            #     schedule_wb, form.batch_number.data, cur_row=cur_row
            # )

        _ = fill_grid(schedule_wb["Расписание"])

        filename_schedule = f"{date.strftime('%Y-%m-%d')} Расписание милкпроджект.xlsx"
        filename_schedule_pickle = f"{date.strftime('%Y-%m-%d')} Расписание милкпроджект.pickle"
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
        BatchNumber.last_batch_number(datetime.today() + timedelta(days=1), "Милкпроджект", group="milk_project") + 1
    )

    return flask.render_template("milk_project/schedule.html", form=form, filename=None)
