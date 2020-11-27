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
from umalat.app.schedule_maker.algo import *
from umalat.config import basedir


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

        excel = ExcelCompiler(path)

        wb.create_sheet('планирование по цехам')

        boiling_request = parse_plan_cell(date=date, wb=wb, excel=excel, skus=skus)
        date = cast_datetime(request['Date'])
        root = make_schedule(request, date)
        schedule_wb = draw_workbook(root, mode='prod', template_fn=os.path.join(basedir, 'app', 'data', 'schedule_tempaltes', 'full_template.xlsx'))

        return jsonify(boiling_request)
    return render_template('schedule.html', form=form)