from app.imports.runtime import *
from flask_wtf.file import FileRequired, FileField
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
    add_auto_boilings = BooleanField(
        "Вставить дополнительные SKU",
        validators=[Optional()],
        default=False,
    )
    date = DateTimeField(
        "Введите дату",
        format="%Y-%m-%d",
        default=datetime.today() + timedelta(days=1),
        validators=[Required()],
    )
