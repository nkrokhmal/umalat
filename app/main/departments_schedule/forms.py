from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired
from app.models import *


class ScheduleForm(FlaskForm):
    date = DateTimeField(
        "Введите дату",
        format="%Y-%m-%d",
        default=datetime.today() + timedelta(days=1),
        validators=[DataRequired()])