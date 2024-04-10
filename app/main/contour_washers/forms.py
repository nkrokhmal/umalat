# fmt: off
import json

from flask_wtf import FlaskForm
from utils_ak.builtin import cast_bool
from wtforms import BooleanField, DateTimeField, FloatField, IntegerField, StringField
from wtforms.validators import DataRequired, Optional

from app.models import *


# todo maybe: better list form


def create_form(request_form, properties):
    class TempForm(FlaskForm):
        pass

    for field, v in json.loads(properties.schema_json(indent=2))["properties"].items():
        if isinstance(v["default"], str):
            setattr(TempForm, properties.department() + '__' + field, StringField(v["description"], validators=[Optional()], default=v["default"]))
        elif isinstance(v["default"], list):
            setattr(TempForm, properties.department() + '__' + field, StringField(v["description"], validators=[Optional()], default=json.dumps(v["default"])))
        elif isinstance(v["default"], bool):
            setattr(TempForm, properties.department() + '__' + field, BooleanField(v["description"], validators=[Optional()], default=v['default']))
        elif isinstance(v["default"], int):
            setattr(TempForm, properties.department() + '__' + field, IntegerField(v["description"], validators=[Optional()], default=v['default']))
        elif isinstance(v["default"], float):
            setattr(TempForm, properties.department() + '__' + field, FloatField(v["description"], validators=[Optional()], default=v['default']))
    return TempForm(request_form)


def fill_properties(form, properties):
    for field, v in json.loads(properties.schema_json(indent=2))["properties"].items():
        if isinstance(v['default'], list):
            setattr(properties, field, json.loads(form[properties.department() + '__' + field]))
        elif v['type'] == 'integer':
            setattr(properties, field, int(form[properties.department() + '__' + field]))
        elif v['type'] == 'boolean':
            setattr(properties, field, cast_bool(form[properties.department() + '__' + field]))
        else:
            setattr(properties, field, form[properties.department() + '__' + field])
    return properties


class ScheduleForm(FlaskForm):
    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[DataRequired()])


class ScheduleDateForm(FlaskForm):
    naslavuchich = BooleanField(
        'Наславучич (ставится в 18:00)',
        validators=[Optional()],
        default=False
    )
    basement_brine = BooleanField(
        "Подвал рассол (ставится в 07:00)",
        validators=[Optional()],
        default=False
    )
    is_today_day_off = BooleanField(
        "Сегодня был нерабочий день",
        validators=[Optional()],
        default=False,
    )
