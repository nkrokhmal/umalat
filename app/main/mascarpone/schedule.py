from flask import render_template, request, current_app
from ..errors import internal_error
from .forms import ScheduleForm
from .. import main
import os
from app.schedule_maker.departments.mascarpone import *
from app.schedule_maker.departments.mascarpone.frontend.style import STYLE

from app.utils.mascarpone.schedule_task import schedule_task_boilings
from app.utils.batches.batch import *
import datetime


@main.route("/mascarpone_schedule", methods=["GET", "POST"])
def mascarpone_schedule():

    form = ScheduleForm(request.form)
    if request.method == "POST" and "submit" in request.form:
        date = form.date.data
        beg_time = form.beg_time.data
        file = request.files["input_file"]

        file_path = os.path.join(current_app.configs["UPLOAD_TMP_FOLDER"], file.filename)
        if file:
            file.save(file_path)
        wb = openpyxl.load_workbook(
            filename=os.path.join(
                current_app.configs["UPLOAD_TMP_FOLDER"], file.filename
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
        frontend = make_frontend(schedule, date=date, start_time=beg_time)
        schedule_wb = draw_excel_frontend(frontend, STYLE, open_file=False, fn=None)
        filename_schedule = f"{date.strftime('%Y-%m-%d')} Расписание маскарпоне.xlsx"

        schedule_wb = schedule_task_boilings(
            schedule_wb, boiling_plan_df, date, form.batch_number.data
        )

        path_schedule = "{}/{}".format("app/data/schedule_plan", filename_schedule)

        schedule_wb.save(path_schedule)
        return render_template(
            "mascarpone/schedule.html", form=form, filename=filename_schedule
        )

    form.date.data = datetime.datetime.today() + datetime.timedelta(days=1)
    form.batch_number.data = (
        BatchNumber.last_batch_number(
            datetime.datetime.today() + datetime.timedelta(days=1),
            "Маскарпоновый цех",
        )
        + 1
    )

    return render_template("mascarpone/schedule.html", form=form, filename=None)
