from app.imports.runtime import *
from flask_wtf.file import FileRequired
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import Required, Optional

from app.models import *


class BoilingPlanForm(FlaskForm):
    validators = [FileRequired(message="Файл не выбран!")]
    input_file = FileField(
        label="Выберите файл",
        validators=validators,
    )
    date = DateTimeField(
        "Введите дату",
        format="%Y-%m-%d",
        default=datetime.today() + timedelta(days=1),
        validators=[Required()],
    )


class ScheduleForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    input_file = FileField("", validators=validators)
    batch_number = IntegerField(
        "Введите номер первой партии в текущем дне", validators=[Optional()]
    )
    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[Required()])
    beg_time = TimeField(
        'Время начала подготовки цеха к работе',
        validators=[Optional()],
        default=time(8, 0),
    )
    add_full_boiling = BooleanField(
        "Вставить полную мойку внутри дня по правилу 12 часов",
        validators=[Optional()],
        default=True,
    )