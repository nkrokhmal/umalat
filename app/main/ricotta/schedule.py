from flask import render_template, request, current_app
from ..errors import internal_error
from .forms import ScheduleForm
from .. import main
from app.schedule_maker import *
import os
from app.schedule_maker.departments.mozarella.frontend import *
from app.utils.mozzarella.schedule_task import schedule_task, schedule_task_boilings
import datetime


@main.route("/ricotta_schedule", methods=["GET", "POST"])
def ricotta_schedule():

    form = ScheduleForm(request.form)
    if request.method == "POST" and "submit" in request.form:
        date = form.date.data
        beg_time = form.beg_time.data
        file = request.files["input_file"]

        # todo: add code!

        return render_template(
            "ricotta/schedule.html", form=form, filename=None
        )

    return render_template(
        "ricotta/schedule.html", form=form, filename=None
    )
