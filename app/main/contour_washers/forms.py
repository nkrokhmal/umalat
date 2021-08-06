# fmt: off
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import Required, Optional
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
            setattr(properties, field, utils.cast_bool(form[properties.department() + '__' + field]))
        else:
            setattr(properties, field, form[properties.department() + '__' + field])
    return properties


class ScheduleForm(FlaskForm):
    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[Required()])


class ScheduleDateForm(FlaskForm):
    milk_project_n_boilings_yesterday = IntegerField(
        "Количество варок в милкпроджект вчера (используется для подсчета скотты)",
        validators=[Optional()],
        default=0,
    )

    adygea_n_boilings_yesterday = IntegerField(
        "Количество варок в адыгейском цехе вчера (используется для подсчета скотты)",
        validators=[Optional()],
        default=0,
    )

    ricotta_n_boilings_yesterday = IntegerField(
        "Количество варок в рикоттном цехе вчера (используется для подсчета скотты)",
        validators=[Optional()],
        default=0,
    )

    molder = BooleanField(
        'Формовщик',
        validators=[Optional()],
        default=False
    )
    is_not_working_day = BooleanField(
        "Завтра нерабочий день",
        validators=[Optional()],
        default=False
    )
    shipping_line = BooleanField(
        "Линия отгрузки",
        validators=[Optional()],
        default=True,
    )
