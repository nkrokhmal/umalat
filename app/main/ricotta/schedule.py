import json
import os

from datetime import datetime, timedelta

import flask
import flask_login
import openpyxl

from utils_ak.openpyxl import write_metadata

from app.main import main
from app.main.ricotta.forms import ScheduleForm
from app.main.ricotta.update_task_and_batches import update_task_and_batches
from app.main.validators import time_validator
from app.models import BatchNumber

# from app.scheduler import *
# from app.utils.batches.batch import *
from app.utils.files.utils import create_if_not_exists, save_schedule, save_schedule_dict

# from app.utils.ricotta.schedule_tasks import schedule_task_boilings, update_total_schedule_task
from app.utils.ricotta.schedule_tasks import RicottaScheduleTask


@main.route("/ricotta_schedule", methods=["GET", "POST"])
@flask_login.login_required
def ricotta_schedule():

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
        first_batch_ids = {"ricotta": form.batch_number.data}
        boiling_plan_df = read_boiling_plan(wb, first_batch_ids=first_batch_ids)

        schedule = make_schedule(boiling_plan_df, start_time=beg_time)
        frontend = wrap_frontend(schedule, date=date)

        schedule_wb = draw_excel_frontend(frontend, STYLE, open_file=False, fn=None, wb=wb)
        write_metadata(schedule_wb, json.dumps({"first_batch_ids": first_batch_ids, "date": str(date)}))

        schedule_task = update_task_and_batches(schedule_wb)

        schedule_wb, _ = schedule_task.schedule_task_original(schedule_wb)
        # schedule_wb, _ = schedule_task.schedule_task_boilings(schedule_wb, form.batch_number.data)

        _ = fill_grid(schedule_wb["Расписание"])

        filename_schedule = f"{date.strftime('%Y-%m-%d')} Расписание рикотта.xlsx"
        filename_schedule_pickle = f"{date.strftime('%Y-%m-%d')} Расписание рикотта.pickle"

        save_schedule(schedule_wb, filename_schedule, date.strftime("%Y-%m-%d"))
        save_schedule_dict(schedule.to_dict(), filename_schedule_pickle, date.strftime("%Y-%m-%d"))

        return flask.render_template(
            "ricotta/schedule.html",
            form=form,
            filename=filename_schedule,
            date=date.strftime("%Y-%m-%d"),
        )

    form.date.data = datetime.today() + timedelta(days=1)
    form.batch_number.data = (
        BatchNumber.last_batch_number(datetime.today() + timedelta(days=1), "Рикоттный цех", group="ricotta") + 1
    )

    return flask.render_template("ricotta/schedule.html", form=form, filename=None)
