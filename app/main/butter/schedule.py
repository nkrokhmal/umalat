import flask

from utils_ak.openpyxl import set_visible_sheets, write_metadata

from app.imports.runtime import *
from app.main import main
from app.main.butter.forms import ScheduleForm
from app.main.butter.update_task_and_batches import update_task_and_batches
from app.main.validators import *
from app.scheduler.butter.draw_frontend.draw_frontend import draw_frontend
from app.scheduler.butter.draw_frontend.style import STYLE
from app.scheduler.butter.to_boiling_plan import to_boiling_plan
from app.scheduler.frontend import fill_grid
from app.utils.batches.batch import *
from app.utils.files.utils import create_if_not_exists, save_schedule, save_schedule_dict


@main.route("/butter_schedule", methods=["GET", "POST"])
@flask_login.login_required
def butter_schedule():
    form = ScheduleForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        # - Unpack form

        date = form.date.data
        beg_time = form.beg_time.data
        batch_number = form.batch_number.data
        file = flask.request.files["input_file"]

        # - Validate time

        time_validator(form, form.beg_time)

        # - Get data dir

        data_dir = os.path.join(
            flask.current_app.config["DYNAMIC_DIR"],
            date.strftime("%Y-%m-%d"),
            flask.current_app.config["BOILING_PLAN_FOLDER"],
        )
        create_if_not_exists(data_dir)

        # - Save file

        file_path = os.path.join(data_dir, file.filename)
        if file:
            file.save(file_path)

        # - Load workbook

        wb = openpyxl.load_workbook(
            filename=os.path.join(data_dir, file.filename),
            data_only=True,
        )

        first_batch_ids_by_type = {"butter": batch_number}

        # - Read boiling plan, generate schedule, frontend and frontend workbook

        _output = draw_frontend(
            boiling_plan=wb, first_batch_ids_by_type=first_batch_ids_by_type, date=date, start_time=beg_time
        )
        schedule, boiling_plan_df, schedule_wb = _output["schedule"], _output["boiling_plan"], _output["workbook"]

        # - Post-process schedule workbook

        write_metadata(schedule_wb, json.dumps({"first_batch_ids": first_batch_ids_by_type, "date": str(date)}))

        filename_schedule = f"{date.strftime('%Y-%m-%d')} Расписание масло.xlsx"
        filename_schedule_pickle = f"{date.strftime('%Y-%m-%d')} Расписание масло.pickle"

        add_batch_from_boiling_plan_df(date, "Масло цех", boiling_plan_df)

        schedule_task = update_task_and_batches(schedule_wb)

        schedule_wb, _ = schedule_task.schedule_task_boilings(schedule_wb)

        _ = fill_grid(schedule_wb["Расписание"])

        set_visible_sheets(
            schedule_wb,
            [
                sn
                for sn in schedule_wb.sheetnames
                if sn in ["Расписание", "Печать заданий", "Печать заданий 2", "План варок"]
            ],
        )

        # - Save schedule workbook and schedule pickle

        save_schedule(schedule_wb, filename_schedule, date.strftime("%Y-%m-%d"))
        save_schedule_dict(schedule.to_dict(), filename_schedule_pickle, date.strftime("%Y-%m-%d"))

        # - Render template

        return flask.render_template(
            "butter/schedule.html",
            form=form,
            filename=filename_schedule,
            date=date.strftime("%Y-%m-%d"),
        )

    # - Init form

    form.date.data = datetime.today() + timedelta(days=1)
    form.batch_number.data = (
        BatchNumber.last_batch_number(datetime.today() + timedelta(days=1), "Масло цех", group="butter") + 1
    )

    # - Render template

    return flask.render_template("butter/schedule.html", form=form, filename=None)
