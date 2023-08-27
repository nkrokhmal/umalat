from app.main import main
from app.main.mascarpone.forms import ScheduleForm
from app.main.mascarpone.update_task_and_batches import update_task_and_batches
from app.main.validators import *
from app.scheduler.mascarpone import *
from app.scheduler.mascarpone.frontend.style import STYLE
from app.utils.batches.batch import *
from app.utils.files.utils import create_if_not_exists, save_schedule, save_schedule_dict
from app.utils.mascarpone.boiling_plan_read import BoilingPlanReader


BATCH_TYPES = ["mascarpone", "cream_cheese", "robiola", "cottage_cheese", "cream"]


@main.route("/mascarpone_schedule", methods=["GET", "POST"])
@flask_login.login_required
def mascarpone_schedule():

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
        first_batch_ids = {
            "mascarpone": form.mascarpone_batch_number.data,
            "cream": form.cream_batch_number.data,
            "robiola": form.robiola_batch_number.data,
            "cream_cheese": form.cream_cheese_batch_number.data,
            "cottage_cheese": form.cottage_cheese_batch_number.data,
        }
        boiling_plan_df = BoilingPlanReader(wb=wb, first_batches=first_batch_ids).parse()

        boiling_plan_df["group"] = boiling_plan_df["sku"].apply(lambda x: x.group.name)

        schedule = make_schedule(boiling_plan_df, start_time=beg_time)
        frontend = wrap_frontend(schedule, date=date)
        schedule_wb = draw_excel_frontend(frontend, STYLE, open_file=False, fn=None, wb=wb)
        utils.write_metadata(schedule_wb, json.dumps({"first_batch_ids": first_batch_ids, "date": str(date)}))

        filename_schedule = f"{date.strftime('%Y-%m-%d')} Расписание маскарпоне.xlsx"
        filename_schedule_pickle = f"{date.strftime('%Y-%m-%d')} Расписание маскарпоне.pickle"

        schedule_task = update_task_and_batches(schedule_wb)
        schedule_wb, _ = schedule_task.schedule_task_original(schedule_wb)
        _ = fill_grid(schedule_wb["Расписание"])
        # schedule_wb, _ = schedule_task.schedule_task_boilings(schedule_wb, form.batch_number.data)

        save_schedule(schedule_wb, filename_schedule, date.strftime("%Y-%m-%d"))
        save_schedule_dict(schedule.to_dict(), filename_schedule_pickle, date.strftime("%Y-%m-%d"))
        return flask.render_template(
            "mascarpone/schedule.html", form=form, filename=filename_schedule, date=date.strftime("%Y-%m-%d")
        )

    form.date.data = datetime.today() + timedelta(days=1)

    for batch_type in BATCH_TYPES:
        getattr(form, f"{batch_type}_batch_number").data = (
            BatchNumber.last_batch_number(
                date=datetime.today() + timedelta(days=1),
                department_name="Маскарпоновый цех",
                group=batch_type,
            )
            + 1
        )

    return flask.render_template("mascarpone/schedule.html", form=form, filename=None)


__all__ = ["mascarpone_schedule"]
