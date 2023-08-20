from datetime import datetime, timedelta

from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class ScheduleForm(FlaskForm):
    date = DateTimeField(
        "Введите дату", format="%Y-%m-%d", default=datetime.today() + timedelta(days=1), validators=[DataRequired()]
    )
