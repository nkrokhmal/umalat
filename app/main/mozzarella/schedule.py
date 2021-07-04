from app.imports.runtime import *
from app.main import main
from app.main.errors import internal_error
from app.scheduler import *
from app.scheduler.mozzarella import *
from app.utils.mozzarella.schedule_task import schedule_task, schedule_task_boilings, update_total_schedule_task
from app.utils.batches.batch import *
from app.utils.mozzarella.parse_schedule_json import prepare_schedule_json
from app.utils.mozzarella.boiling_plan_draw import draw_boiling_plan_merged
from app.utils.mozzarella.additional_packing_draw import draw_additional_packing
from app.utils.features.openpyxl_wrapper import set_default_sheet
from app.utils.files.utils import save_schedule, save_schedule_dict
from .forms import ScheduleForm


@main.route("/mozzarella_schedule", methods=["GET", "POST"])
@flask_login.login_required
def mozzarella_schedule():
    form = ScheduleForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        date = form.date.data
        add_full_boiling = form.add_full_boiling.data

        file = flask.request.files["input_file"]
        file_path = os.path.join(flask.current_app.config["UPLOAD_TMP_FOLDER"], file.filename)
        if file:
            file.save(file_path)
        wb = openpyxl.load_workbook(
            filename=os.path.join(
                flask.current_app.config["UPLOAD_TMP_FOLDER"], file.filename
            ),
            data_only=True,
        )

        boiling_plan_df = cast_boiling_plan(wb)
        additional_packing_df = read_additional_packing(wb)
        # todo: check boiling_plan_task

        add_batch(
            date,
            "Моцарельный цех",
            form.batch_number.data,
            form.batch_number.data + int(boiling_plan_df["group_id"].max()) - 1,
        )

        start_times = {
            LineName.WATER: form.water_beg_time.data,
            LineName.SALT: form.salt_beg_time.data,
        }

        schedule = make_schedule(
            boiling_plan_df,
            start_times=start_times,
            optimize=add_full_boiling,
            first_boiling_id=int(form.batch_number.data),
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
        cleanings = ([
            x
            for x in schedule_json["children"][0]["children"]
            if x["cls"] == "cleaning"
        ])
        schedule_df = prepare_schedule_json(schedule_json, cleanings)

        schedule_wb = openpyxl.load_workbook(
            filename=flask.current_app.config["TEMPLATE_SCHEDULE_PLAN"]
        )
        schedule_wb = draw_boiling_plan_merged(schedule_df, schedule_wb)
        schedule_wb = draw_excel_frontend(
            frontend, open_file=False, fn=None, style=STYLE, wb=schedule_wb,
        )

        filename_schedule = "{} {}.xlsx".format(date.strftime("%Y-%m-%d"), "Расписание моцарелла")
        filename_schedule_json = "{} {}.json".format(date.strftime("%Y-%m-%d"), "Расписание моцарелла")

        update_total_schedule_task(date, boiling_plan_df, additional_packing_df)
        schedule_wb = schedule_task(schedule_wb, boiling_plan_df, additional_packing_df, date)
        schedule_wb = schedule_task_boilings(
            schedule_wb, boiling_plan_df, additional_packing_df, date, form.batch_number.data
        )
        schedule_wb = draw_additional_packing(schedule_wb, additional_packing_df)
        set_default_sheet(schedule_wb)

        save_schedule(schedule_wb, filename_schedule, date.strftime("%Y-%m-%d"))
        # save_schedule_dict(schedule_json, filename_schedule_json, date.strftime("%Y-%m-%d"))
        os.remove(file_path)

        return flask.render_template(
            "mozzarella/schedule.html", form=form, filename=filename_schedule, date=date.strftime("%Y-%m-%d")
        )

    form.date.data = datetime.today() + timedelta(days=1)
    form.batch_number.data = (
        BatchNumber.last_batch_number(
            datetime.today() + timedelta(days=1),
            "Моцарельный цех",
        )
        + 1
    )
    filename_schedule = None

    return flask.render_template(
        "mozzarella/schedule.html", form=form, filename=filename_schedule
    )
