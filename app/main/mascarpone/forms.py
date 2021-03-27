from flask_restplus import ValidationError
from flask_wtf.file import FileRequired, FileField
from wtforms import (
    StringField,
    SubmitField,
    BooleanField,
    SelectField,
    IntegerField,
    FloatField,
    DateTimeField,
    TimeField,
)
from wtforms.validators import Required, Optional
from flask_wtf import FlaskForm

from ...models import (
    Packer,
    RicottaBoiling,
    RicottaLine,
    PackType,
    FormFactor,
    RicottaSKU,
    RicottaBoilingTechnology,
    Group,
    BatchNumber,
    RicottaFormFactor,
)
from ... import db
import datetime


class BoilingPlanForm(FlaskForm):
    validators = [FileRequired(message="Файл не выбран!")]
    input_file = FileField(
        label="Выберите файл",
        validators=validators,
    )
    date = DateTimeField(
        "Введите дату",
        format="%Y-%m-%d",
        default=datetime.datetime.today() + datetime.timedelta(days=1),
        validators=[Required()],
    )
