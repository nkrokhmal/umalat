from flask import render_template, request, current_app
from ..errors import internal_error
from .forms import ScheduleForm
from .. import main
from app.schedule_maker import *
import os
from app.schedule_maker.departments.ricotta import *

import datetime


@main.route("/ricotta_schedule", methods=["GET", "POST"])
def ricotta_schedule():

    form = ScheduleForm(request.form)
    if request.method == "POST" and "submit" in request.form:
        date = form.date.data
        beg_time = form.beg_time.data
        file = request.files["input_file"]

        file_path = os.path.join(current_app.config["UPLOAD_TMP_FOLDER"], file.filename)
        if file:
            file.save(file_path)
        wb = openpyxl.load_workbook(
            filename=os.path.join(
                current_app.config["UPLOAD_TMP_FOLDER"], file.filename
            ),
            data_only=True,
        )
        boiling_plan_df = read_boiling_plan(wb)
        schedule = make_schedule(boiling_plan_df)
        frontend = make_frontend(schedule, date=date, start_time=beg_time)
        schedule_wb = draw_excel_frontend(
            frontend, RICOTTA_STYLE, open_file=False, fn=None
        )

        return render_template("ricotta/schedule.html", form=form, filename=None)

    return render_template("ricotta/schedule.html", form=form, filename=None)
