import os
from flask import render_template, request

from ..errors import internal_error
from app.utils.old.excel_client import *
from .. import main
from .forms import ScheduleForm

from utils_ak.interactive_imports import *
from app.schedule_maker import *

from app.schedule_maker.frontend import *
from ...utils.schedule_task import schedule_task, schedule_task_boilings


def add_batch(date, beg_number, end_number):
    batch = BatchNumber.get_batch_by_date(date)
    if batch is not None:
        batch.beg_number = beg_number
        batch.end_number = end_number
    else:
        batch = BatchNumber(
            datetime=date,
            beg_number=beg_number,
            end_number=end_number,
        )
        db.session.add(batch)
    db.session.commit()


@main.route('/schedule', methods=['GET', 'POST'])
def schedule():
    form = ScheduleForm(request.form)
    if request.method == 'POST' and 'submit' in request.form:
        date = form.date.data
        add_full_boiling = form.add_full_boiling.data

        file = request.files['input_file']
        file_path = os.path.join(current_app.config['UPLOAD_TMP_FOLDER'], file.filename)
        if file:
            file.save(file_path)
        wb = openpyxl.load_workbook(filename=os.path.join(current_app.config['UPLOAD_TMP_FOLDER'], file.filename),
                                    data_only=True)

        boiling_plan_df = read_boiling_plan(wb)
        add_batch(date, form.batch_number.data, form.batch_number.data + int(boiling_plan_df['group_id'].max()))
        start_times = {LineName.WATER: form.water_beg_time.data, LineName.SALT: form.salt_beg_time.data}

        if add_full_boiling:
            schedule = make_schedule_with_boiling_inside_a_day(boiling_plan_df, start_times=start_times, first_group_id=form.batch_number.data, date=date)
        else:
            boilings = make_boilings(boiling_plan_df, first_group_id=form.batch_number.data)
            cleanings = boiling_plan_df.groupby('group_id').agg({'cleaning': 'first'}).to_dict()['cleaning']
            cleanings = {k + int(form.batch_number.data) - 1: v for k, v in cleanings.items() if v}
            schedule = make_schedule(boilings, cleanings=cleanings, start_times=start_times, date=date)

        try:
            frontend = make_frontend(schedule)
        except Exception as e:
            return internal_error(e)
            # raise Exception('Ошибка при построении расписания.')

        schedule_wb = draw_excel_frontend(frontend, open_file=False, fn=None)

        filename_schedule = '{} {}.xlsx'.format(date.strftime('%Y-%m-%d'), 'Расписание')

        schedule_wb = schedule_task(schedule_wb, boiling_plan_df, date)
        schedule_wb = schedule_task_boilings(schedule_wb, boiling_plan_df, date, form.batch_number.data)

        path_schedule = '{}/{}'.format('app/data/schedule_plan', filename_schedule)
        schedule_wb.save(path_schedule)

        os.remove(file_path)
        return render_template('mozzarella/schedule.html', form=form, filename=filename_schedule)

    form.date.data = datetime.datetime.today() + datetime.timedelta(days=1)
    form.batch_number.data = BatchNumber.last_batch_number(
        datetime.datetime.today() + datetime.timedelta(days=1)
    ) + 1
    filename_schedule = None
    return render_template('mozzarella/schedule.html', form=form, filename=filename_schedule)
