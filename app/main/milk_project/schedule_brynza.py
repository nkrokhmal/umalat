import os

from datetime import datetime, timedelta

import flask
import flask_login

from utils_ak import openpyxl

from app.imports.runtime import db
from app.main import main
from app.main.milk_project.forms import BrynzaScheduleForm
from app.models import BatchNumber, BrynzaSKU
from app.scheduler.brynza.draw_frontend2.draw_frontend2 import draw_frontend2
from app.scheduler.frontend_utils import fill_grid
from app.utils.files.utils import create_if_not_exists, save_schedule, save_schedule_dict


class BrynzaScheduleException(Exception):
    ...


def round_to_base(number, base):
    rounded_number_in_base = round(number / base) * base
    rounded_number = rounded_number_in_base
    return rounded_number


@main.route("/brynza_schedule", methods=["GET", "POST"])
@flask_login.login_required
def brynza_schedule():
    form = BrynzaScheduleForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        date = form.date.data
        beg_time = form.beg_time.data
        brynza_kg = form.brynza_kg.data
        chanakh_kg = form.chanakh_kg.data

        skus = db.session.query(BrynzaSKU).all()
        chanakh_output = [sku for sku in skus if sku.group.name == "Чанах"][0].made_from_boilings[0].output_kg
        brynza_output = [sku for sku in skus if sku.group.name == "Брынза"][0].made_from_boilings[0].output_kg
        if abs(brynza_kg - round_to_base(brynza_kg, brynza_output)) > 50:
            raise BrynzaScheduleException("Значение входа брынзы превышает допустимую погрешность в 50 кг")

        if abs(chanakh_kg - round_to_base(chanakh_kg, chanakh_output)) > 50:
            raise BrynzaScheduleException("Значение входа чаназа превышает допустимую погрешность в 50 кг")

        brynza_kg = round_to_base(brynza_kg, brynza_output) / brynza_output * 3150
        chanakh_kg = round_to_base(chanakh_kg, chanakh_output) / chanakh_output * 3150

        print(f"Chanakh input {brynza_kg}")
        print(f"Brynza input {chanakh_kg}")

        data_dir = os.path.join(
            flask.current_app.config["DYNAMIC_DIR"],
            date.strftime("%Y-%m-%d"),
            flask.current_app.config["BOILING_PLAN_FOLDER"],
        )
        create_if_not_exists(data_dir)

        output = draw_frontend2(
            brynza_kg=brynza_kg,
            chanah_kg=chanakh_kg,
            first_batch_ids_by_type={"brynza": form.batch_number.data},
            date=date,
            workbook=None,
        )

        schedule, schedule_wb = output["schedule"], output["workbook"]

        # write_metadata(schedule_wb, json.dumps({"first_batch_ids": first_batch_ids_by_type, "date": str(date)}))

        filename_schedule = f"{date.strftime('%Y-%m-%d')} Расписание брынзы.xlsx"
        filename_schedule_pickle = f"{date.strftime('%Y-%m-%d')} Расписание брынзы.pickle"

        # schedule_task = update_task_and_batches(schedule_wb)
        # schedule_wb, _ = schedule_task.schedule_task_original(schedule_wb)
        _ = fill_grid(schedule_wb["Расписание"])
        # schedule_wb, _ = schedule_task.schedule_task_boilings(schedule_wb, form.batch_number.data)

        save_schedule(schedule_wb, filename_schedule, date.strftime("%Y-%m-%d"))
        save_schedule_dict(schedule.to_dict(), filename_schedule_pickle, date.strftime("%Y-%m-%d"))

        return flask.render_template(
            "milk_project/schedule_brynza.html",
            form=form,
            filename=filename_schedule,
            date=date.strftime("%Y-%m-%d"),
        )

    form.date.data = datetime.today() + timedelta(days=1)
    form.batch_number.data = (
        BatchNumber.last_batch_number(
            date=datetime.today() + timedelta(days=1),
            department_name="Милкпроджект",
            group="brynza",
        )
        + 1
    )

    return flask.render_template("milk_project/schedule_brynza.html", form=form, filename=None)
