import flask

from app.imports.runtime import *

from app.main import main
from app.main.errors import internal_error
from app.scheduler.mascarpone import *
from app.scheduler.mascarpone.frontend.style import STYLE
from app.utils.mascarpone.schedule_task import MascarponeScheduleTask
from app.utils.batches.batch import *
from app.scheduler import draw_excel_frontend
from app.utils.files.utils import save_schedule, save_schedule_dict, create_if_not_exists
from .forms import ScheduleForm


MASCARPONE_GROUPS = [
    ('mascarpone_batch_number', 'Маскарпоне'),
    ('cream_cheese_batch_number', 'Кремчиз'),
    ('robiola_batch_number', 'Робиола'),
    ('cottage_cheese_batch_number', 'Творожный'),
    ('cream_batch_number', 'Сливки'),
]

@main.route("/mascarpone_schedule", methods=["GET", "POST"])
@flask_login.login_required
def mascarpone_schedule():

    form = ScheduleForm(flask.request.form)
    if flask.request.method == "POST" and "submit" in flask.request.form:
        date = form.date.data
        beg_time = form.beg_time.data
        file = flask.request.files["input_file"]

        # Маскарпоне, кремчиз, робиолла, творожный, сливки
        mascarpone_batch_number = form.mascarpone_batch_number.data
        cream_batch_number = form.cream_batch_number.data
        robiola_batch_number = form.robiola_batch_number.data
        cream_cheese_batch_number = form.cream_cheese_batch_number.data
        cottage_cheese_batch_number = form.cottage_cheese_batch_number.data

        # todo next: make properly @nkrokhmal
        batch_number = mascarpone_batch_number

        data_dir = os.path.join(
            flask.current_app.config["DYNAMIC_DIR"],
            date.strftime("%Y-%m-%d"),
            flask.current_app.config["BOILING_PLAN_FOLDER"])
        create_if_not_exists(data_dir)

        file_path = os.path.join(data_dir, file.filename)
        if file:
            file.save(file_path)
        wb = openpyxl.load_workbook(
            filename=os.path.join(
                data_dir, file.filename
            ),
            data_only=True,
        )
        boiling_plan_df = read_boiling_plan(wb)
        boiling_plan_df['group'] = boiling_plan_df['sku'].apply(lambda x: x.group.name)

        for attr, group in MASCARPONE_GROUPS:
            boiling_plan_grouped = boiling_plan_df.groupby("boiling_id").agg({"group": "first"})
            boilings_grouped = boiling_plan_grouped[boiling_plan_grouped["group"] == group].count()
            if int(boilings_grouped) > 0:
                add_batch(
                    date=date,
                    department_name="Маскарпоновый цех",
                    beg_number=getattr(form, attr).data,
                    end_number=getattr(form, attr).data + int(boilings_grouped) - 1,
                    group=group,
                )

        schedule = make_schedule(boiling_plan_df,
                                 mascarpone_batch_number,
                                 cream_batch_number,
                                 robiola_batch_number,
                                 cream_cheese_batch_number,
                                 cottage_cheese_batch_number, start_time=beg_time)
        frontend = wrap_frontend(schedule, date=date)
        schedule_template = openpyxl.load_workbook(
            filename=flask.current_app.config["TEMPLATE_SCHEDULE_PLAN_DEPARTMENT"],
            data_only=True,
        )
        schedule_wb = draw_excel_frontend(frontend, STYLE, open_file=False, fn=None, wb=schedule_template)
        filename_schedule = f"{date.strftime('%Y-%m-%d')} Расписание маскарпоне.xlsx"
        filename_schedule_pickle = f"{date.strftime('%Y-%m-%d')} Расписание маскарпоне.pickle"

        schedule_task = MascarponeScheduleTask(
            df=boiling_plan_df,
            date=date,
            model=MascarponeSKU,
            department="Маскарпонный цех"
        )

        schedule_task.update_total_schedule_task()
        schedule_task.update_boiling_schedule_task(batch_number)

        schedule_wb, _ = schedule_task.schedule_task_original(schedule_wb)
        # schedule_wb, _ = schedule_task.schedule_task_boilings(schedule_wb, form.batch_number.data)

        save_schedule(schedule_wb, filename_schedule, date.strftime("%Y-%m-%d"))
        save_schedule_dict(schedule.to_dict(), filename_schedule_pickle, date.strftime("%Y-%m-%d"))
        return flask.render_template(
            "mascarpone/schedule.html", form=form, filename=filename_schedule, date=date.strftime("%Y-%m-%d")
        )

    form.date.data = datetime.today() + timedelta(days=1)
    for attr, group in MASCARPONE_GROUPS:
        getattr(form, attr).data = BatchNumber.last_batch_number(
            date=datetime.today() + timedelta(days=1),
            department_name="Маскарпоновый цех",
            group=group,
        ) + 1

    return flask.render_template("mascarpone/schedule.html", form=form, filename=None)
