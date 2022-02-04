from app.imports.runtime import *
from app.main import main
from app.main.errors import internal_error
from app.scheduler import *
from app.scheduler.mozzarella import *
from app.utils.mozzarella.schedule_task import MozzarellaScheduleTask
from app.utils.batches.batch import *
from app.utils.mozzarella.parse_schedule_json import *
from app.utils.mozzarella.boiling_plan_draw import draw_boiling_plan_merged
from app.utils.mozzarella.additional_packing_draw import draw_additional_packing
from app.utils.features.openpyxl_wrapper import set_default_sheet
from app.main.mozzarella.update_task_and_batches import update_task_and_batches
from app.utils.files.utils import (
    save_schedule,
    save_schedule_dict,
    create_if_not_exists,
)
from app.main.validators import *
from .forms import ScheduleForm


@main.route("/mozzarella_schedule", methods=["GET", "POST"])
@flask_login.login_required
def mozzarella_schedule():
    form = ScheduleForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        date = form.date.data
        add_full_boiling = form.add_full_boiling.data
        optimize = form.optimize.data

        # validate time
        time_validator(form, form.water_beg_time)
        time_validator(form, form.salt_beg_time)

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
        first_batch_ids = {'mozzarella': form.batch_number.data}
        boiling_plan_df = cast_boiling_plan(wb, first_batch_ids=first_batch_ids)
        additional_packing_df = read_additional_packing(wb)

        start_times = {
            LineName.WATER: form.water_beg_time.data,
            LineName.SALT: form.salt_beg_time.data,
        }


        schedule = make_schedule(
            boiling_plan_df,
            start_times=start_times,
            optimize=optimize,
            optimize_cleanings=add_full_boiling,
            date=date,
        )

        try:
            frontend = wrap_frontend(schedule)
        except Exception as e:
            return internal_error(e)
            # raise Exception('Ошибка при построении расписания.')

        schedule_json = schedule.to_dict(
            props=[
                {"key": "x", "value": lambda b: list(b.props["x"])},
                {"key": "size", "value": lambda b: list(b.props["size"])},
                {"key": "cleaning_type", "cls": "cleaning"},
                {
                    "key": "boiling_group_df",
                    "cls": "boiling",
                },
            ]
        )
        cleanings = [
            x
            for x in schedule_json["children"][0]["children"]
            if x["cls"] == "cleaning"
        ]
        schedule_df = prepare_schedule_json(schedule_json, cleanings)

        schedule_wb = openpyxl.load_workbook(
            filename=flask.current_app.config["TEMPLATE_SCHEDULE_PLAN"]
        )

        schedule_wb = draw_boiling_plan_merged(schedule_df, schedule_wb)
        schedule_wb = draw_excel_frontend(
            frontend,
            open_file=False,
            fn=None,
            style=STYLE,
            wb=schedule_wb,
        )
        schedule_wb = draw_additional_packing(schedule_wb, additional_packing_df)
        utils.write_metadata(schedule_wb, json.dumps({'first_batch_ids': first_batch_ids, 'date': str(date)}))

        schedule_task = update_task_and_batches(schedule_wb, boiling_plan_df=boiling_plan_df)

        schedule_wb = schedule_task.schedule_task_original(schedule_wb)
        schedule_wb = schedule_task.schedule_task_boilings(schedule_wb)

        set_default_sheet(schedule_wb)

        filename_schedule = "{} {}.xlsx".format(
            date.strftime("%Y-%m-%d"), "Расписание моцарелла"
        )
        filename_schedule_pickle = "{} {}.pickle".format(
            date.strftime("%Y-%m-%d"), "Расписание моцарелла"
        )

        save_schedule(schedule_wb, filename_schedule, date.strftime("%Y-%m-%d"))
        save_schedule_dict(
            schedule.to_dict(), filename_schedule_pickle, date.strftime("%Y-%m-%d")
        )

        return flask.render_template(
            "mozzarella/schedule.html",
            form=form,
            filename=filename_schedule,
            date=date.strftime("%Y-%m-%d"),
        )

    form.date.data = datetime.today() + timedelta(days=1)

    form.batch_number.data = (
        BatchNumber.last_batch_number(
            datetime.today() + timedelta(days=1),
            "Моцарельный цех",
            group='mozzarella'
        )
        + 1
    )
    filename_schedule = None

    return flask.render_template(
        "mozzarella/schedule.html", form=form, filename=filename_schedule
    )
