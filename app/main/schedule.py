import os
from flask import session, url_for, render_template, flash, request, make_response, current_app, request, jsonify

from .errors import internal_error
from .. utils.excel_client import *
from . import main
from .. import db
from .forms import ScheduleForm
import io
import openpyxl
from pycel import ExcelCompiler

from utils_ak.interactive_imports import *
from app.schedule_maker import *
from app.enum import LineName

from config import basedir

from app.schedule_maker.frontend import *
import datetime


@main.route('/schedule', methods=['GET', 'POST'])
def schedule():
    try:
        form = ScheduleForm()
        if request.method == 'POST' and form.validate_on_submit():
            date = form.date.data
            file = request.files['input_file']
            file_path = os.path.join(current_app.config['UPLOAD_TMP_FOLDER'], file.filename)
            if file:
                file.save(file_path)
            wb = openpyxl.load_workbook(filename=os.path.join(current_app.config['UPLOAD_TMP_FOLDER'], file.filename),
                                        data_only=True)

            boiling_plan_df = read_boiling_plan(wb)
            start_times = {LineName.WATER: form.water_beg_time.data, LineName.SALT: form.salt_beg_time.data}

            # boilings = make_boilings_by_groups(boiling_plan_df)
            # schedule = make_schedule(boilings, start_times=start_times)

            schedule = make_schedule_with_boiling_inside_a_day(boiling_plan_df, start_times=start_times)

            try:
                frontend = make_frontend(schedule)
            except Exception as e:
                return internal_error(e)
                # raise Exception('Ошибка при построении расписания.')

            schedule_wb = draw_excel_frontend(frontend, open_file=False, fn=None)

            filename_schedule = '{} {}.xlsx'.format(date.strftime('%Y-%m-%d'), 'Расписание')
            path_schedule = '{}/{}'.format('app/data/schedule_plan', filename_schedule)
            schedule_wb.save(path_schedule)
            os.remove(file_path)
            return render_template('schedule.html', form=form, filename=filename_schedule)

        filename_schedule = None
        return render_template('schedule.html', form=form, filename=filename_schedule)

    except Exception as e:
        db.session.rollback()
        return internal_error(e)
