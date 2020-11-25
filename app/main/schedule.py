from flask import session, url_for, render_template, flash, request, make_response, current_app, request, jsonify
from .. utils.excel_client import *
from . import main
from .. import db
from .forms import ScheduleForm
from ..models import SKU
import io
import openpyxl
from pycel import ExcelCompiler


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
        response = parse_plan_cell(date=date, wb=wb, excel=excel, skus=skus)
        return jsonify(response)
    return render_template('schedule.html', form=form)