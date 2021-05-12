from app.imports.runtime import *

from app.main import main
from app.main.errors import internal_error
from app.schedule_maker import *
from app.schedule_maker.departments.mozarella import *
from app.utils.mozzarella.schedule_task import schedule_task, schedule_task_boilings
from app.utils.batches.batch import *


from .forms import ScheduleForm


@main.route("/schedule", methods=["GET", "POST"])
def schedule():

    form = ScheduleForm(request.form)
    if request.method == "POST" and "submit" in request.form:
        date = form.date.data
        add_full_boiling = form.add_full_boiling.data

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

        boiling_plan_df = cast_boiling_plan(wb)
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
            first_group_id=int(form.batch_number.data),
        )

        try:
            frontend = make_frontend(schedule)
        except Exception as e:
            return internal_error(e)
            # raise Exception('Ошибка при построении расписания.')

        schedule_wb = draw_excel_frontend(
            frontend, open_file=False, fn=None, style=STYLE
        )

        filename_schedule = "{} {}.xlsx".format(date.strftime("%Y-%m-%d"), "Расписание")

        schedule_wb = schedule_task(schedule_wb, boiling_plan_df, date)
        schedule_wb = schedule_task_boilings(
            schedule_wb, boiling_plan_df, date, form.batch_number.data
        )

        path_schedule = "{}/{}".format("app/data/schedule_plan", filename_schedule)
        schedule_wb.save(path_schedule)

        os.remove(file_path)

        return render_template(
            "mozzarella/schedule.html", form=form, filename=filename_schedule
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

    return render_template(
        "mozzarella/schedule.html", form=form, filename=filename_schedule
    )
