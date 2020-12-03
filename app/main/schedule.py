from flask import session, url_for, render_template, flash, request, make_response, current_app, request, jsonify
from .. utils.excel_client import *
from . import main
from .. import db
from .forms import ScheduleForm
from ..models import SKU
import io
import openpyxl
from pycel import ExcelCompiler

from utils_ak.interactive_imports import *
from app.schedule_maker.algo import *
from config import basedir
import datetime



@main.route('/schedule', methods=['GET', 'POST'])
def schedule():
    form = ScheduleForm()
    print('Schedule function started')
    if request.method == 'POST' and form.validate_on_submit():

        date = form.date.data
        skus = db.session.query(SKU).all()
        file_bytes = request.files['input_file'].read()
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes))

        filename = '{}_{}.xlsx'.format('schedule', date.strftime('%Y-%m-%d'))
        path = '{}/{}'.format('app/data/schedule', filename)
        wb.save(path)

        filename_schedule = '{}_{}.xlsx'.format('schedule', date.strftime('%Y-%m-%d'))
        json_schedule = '{}_{}.txt'.format('schedule', date.strftime('%Y-%m-%d'))

        path_schedule = '{}/{}'.format('app/data/schedule', filename_schedule)
        path_json_schedule = '{}/{}'.format('app/data/schedule_json', json_schedule)

        excel = ExcelCompiler(path)

        wb.create_sheet('планирование по цехам')

        boiling_request = parse_plan_cell(date=date, wb=wb, excel=excel, skus=skus)
        with open(path_json_schedule, 'w') as outfile:
            def default(o):
                if isinstance(o, (datetime.date, datetime.datetime)):
                    return o.isoformat()
            json.dump(boiling_request, outfile, default=default)

        root = make_schedule(boiling_request, date)
        schedule_wb = draw_workbook(root, mode='prod')
        schedule_wb.save(path_schedule)

        schedule_link = '{}/{}'.format('data/schedule', filename_schedule)
        schedule_json_link = '{}/{}'.format('data/schedule_json', json_schedule)
        return render_template('schedule.html', form=form, schedule_link=schedule_link, schedule_json_link=schedule_json_link)
    schedule_link = None
    schedule_json_link = None
    return render_template('schedule.html', form=form, schedule_link=schedule_link, schedule_json_link=schedule_json_link)