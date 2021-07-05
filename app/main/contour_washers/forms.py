from app.imports.runtime import *
from flask_wtf.file import FileRequired, FileField
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import Required, Optional

from app.models import *


class ScheduleForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    input_file = FileField("", validators=validators)
    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[Required()])