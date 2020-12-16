from io import BytesIO
from flask import url_for, render_template, flash, request, make_response, current_app, request
from werkzeug.utils import redirect
from . import main
import pandas as pd
from .. import db
from .forms import StatisticForm
from ..models import SKU, Boiling
from sqlalchemy import or_, and_
from flask_restplus import reqparse
import openpyxl
from app.interactive_imports import *
import re
import numpy as np
from .. utils.generate_constructor import *


# todo: add plan
# todo: file naming
@main.route('/generate_boiling_plan', methods=['POST', 'GET'])
def generate_boiling_plan():
    form = StatisticForm()
    if request.method == 'POST' and form.validate_on_submit():
        file = request.files['input_file']
        file_name = file.filename
        file_data = BytesIO(file.read())
        df = pd.read_csv(file_data)
        df['sku'] = df['sku'].apply(cast_sku)
        df = df.replace(to_replace='None', value=np.nan).dropna()
        df['boiling_id'] = df['sku'].apply(lambda x: x.boilings[0].id)
        df['sku_id'] = df['sku'].apply(lambda x: x.id)
        df['plan'] = df['plan'].apply(lambda x: -float(x))
        df = df[['boiling_id', 'sku_id', 'plan']]
        df['sku'] = df['sku_id'].apply(cast_sku)
        boiling_plan_df = generate_constructor_df(df)
        full_plan = generate_full_constructor_df(boiling_plan_df)
        link = draw_constructor(full_plan, file_name)
        return render_template('boiling_plan.html', form=form, link=link)
    link = None
    return render_template('boiling_plan.html', form=form, link=link)
