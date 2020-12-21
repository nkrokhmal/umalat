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

from app.schedule_maker.frontend import *


@main.route('/schedule', methods=['GET', 'POST'])
def schedule():
    form = ScheduleForm()
    if request.method == 'POST' and form.validate_on_submit():
        date = form.date.data
        skus = db.session.query(SKU).all()
        file_bytes = request.files['input_file'].read()
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes))
        boiling_plan_df = load_boiling_plan(wb)
        schedule_wb = create_excel_frontend(boiling_plan_df)
        filename = '{}_{}.xlsx'.format('schedule', date.strftime('%Y-%m-%d'))
        filename_schedule = '{}_{}.xlsx'.format('schedule', date.strftime('%Y-%m-%d'))
        path_schedule = '{}/{}'.format('app/data/schedule', filename_schedule)
        schedule_wb.save(path_schedule)
        return render_template('schedule.html', form=form, filename=filename)
    filename = None
    return render_template('schedule.html', form=form, filename=filename)
