from app.imports.runtime import *
from flask_wtf.file import FileRequired, FileField
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import Required, Optional

from app.models import *


class ScheduleForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[Required()])

    butter_end_time = TimeField(
        "Время окончания работы маслоцеха по умолчанию",
        validators=[Optional()],
        default=time(19, 0),
    )
    milk_project_end_time = TimeField(
        "Время окончания работы милкпроджекта по умолчанию",
        validators=[Optional()],
        default=time(11, 0),
    )
    adygea_end_time = TimeField(
        "Время окончания работы адыгейского цеха по умолчанию",
        validators=[Optional()],
        default=time(14, 0),
    )

    is_not_working_day = BooleanField(
        "Завтра нерабочий день",
        validators=[Optional()],
        default=False,
    )
