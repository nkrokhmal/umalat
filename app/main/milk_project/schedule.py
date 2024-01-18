import flask
import flask_login
import openpyxl

from utils_ak.openpyxl import draw_sheet_sequence, write_metadata

from app.main import main
from app.main.adygea.update_task_and_batches import update_task_and_batches as update_task_and_batches_adygea
from app.main.milk_project.forms import ScheduleForm
from app.main.milk_project.update_task_and_batches import (
    update_task_and_batches as update_task_and_batches_milk_project,
)
from app.main.validators import *
from app.models import BrynzaSKU
from app.scheduler.adygea.draw_frontend.draw_frontend import draw_frontend as draw_frontend_adygea
from app.scheduler.brynza.draw_frontend.draw_frontend import draw_frontend as draw_frontend_brynza
from app.scheduler.frontend_utils import fill_grid
from app.scheduler.time_utils import *
from app.utils.base.schedule_task import BaseScheduleTask
from app.utils.batches.batch import *
from app.utils.files.utils import create_if_not_exists, save_schedule, save_schedule_dict


@main.route("/milk_project_schedule", methods=["GET", "POST"])
@flask_login.login_required
def milk_project_schedule():
    form = ScheduleForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        date = form.date.data
        beg_time = form.beg_time.data
        packing_beg_time = form.packing_beg_time.data

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

        # Delete list "Расписание" if exists
        if "Расписание" in wb.sheetnames:
            wb.remove(wb["Расписание"])

        first_batch_ids = {"milk_project": form.batch_number.data}

        adygea_output = draw_frontend_adygea(boiling_plan=wb, start_time=beg_time, workbook=wb, date=date)
        adygea_schedule, adygea_schedule_wb = adygea_output["schedule"], adygea_output["workbook"]
        if len(adygea_output["boiling_plan_df"]) > 0 and len(adygea_output["boiling_plan_df"]) > 0:
            # Set preferred header time"
            adygea_output["schedule"].props.update(preferred_header_time=cast_time(adygea_output["schedule"].x[0]))

        brynza_output = draw_frontend_brynza(boiling_plan=wb, date=date, start_time=packing_beg_time)
        brynza_schedule, brynza_schedule_wb = brynza_output["schedule"], brynza_output["workbook"]

        draw_sheet_sequence(
            (wb, "Расписание"), [(adygea_schedule_wb, "Расписание"), (brynza_schedule_wb, "Расписание")]
        )

        write_metadata(adygea_schedule_wb, json.dumps({"first_batch_ids": first_batch_ids, "date": str(date)}))

        schedule_tasks = [
            update_task_and_batches_milk_project(adygea_schedule_wb),
            update_task_and_batches_adygea(adygea_schedule_wb),
        ]

        cur_row = 2
        for schedule_task in schedule_tasks:
            adygea_schedule_wb, cur_row = schedule_task.schedule_task_original(adygea_schedule_wb, cur_row=cur_row)

        brynza_df = brynza_output["brynza_boiling_plan_df"]
        brynza_df["absolute_batch_id"] = brynza_df["batch_id"]
        brynza_df[["start", "finish"]] = "", ""
        brynza_task = BaseScheduleTask(brynza_df, date=date, model=BrynzaSKU, department="Брынза")
        brynza_task.schedule_task_original(adygea_schedule_wb, cur_row=cur_row)
        brynza_task.update_schedule_task()

        _ = fill_grid(adygea_schedule_wb["Расписание"])

        filename_schedule = f"{date.strftime('%Y-%m-%d')} Расписание милкпроджект.xlsx"
        filename_schedule_pickle = f"{date.strftime('%Y-%m-%d')} Расписание милкпроджект.pickle"
        save_schedule(adygea_schedule_wb, filename_schedule, date.strftime("%Y-%m-%d"))
        save_schedule_dict(
            adygea_output["schedule"].to_dict(),
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
