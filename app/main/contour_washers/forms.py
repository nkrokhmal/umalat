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
            setattr(TempForm, field, StringField(v["description"], validators=[Optional()], default=v["default"]))
        elif isinstance(v["default"], list):
            setattr(TempForm, field, StringField(v["description"], validators=[Optional()], default=json.dumps(v["default"])))
        elif isinstance(v["default"], bool):
            setattr(TempForm, field, BooleanField(v["description"], validators=[Optional()], default=v['default']))
        elif isinstance(v["default"], int):
            setattr(TempForm, field, IntegerField( v["description"], validators=[Optional()], default=v['default']))
        elif isinstance(v["default"], float):
            setattr(TempForm, field, FloatField(v["description"], validators=[Optional()], default=v['default']))
    return TempForm(request_form)


def fill_properties(form, properties):
    for field, v in json.loads(properties.schema_json(indent=2))["properties"].items():
        if isinstance(v['default'], list):
            # todo maybe: make properly
            setattr(properties, field, json.loads(getattr(form, field).data.replace("'", '"')))
        else:
            setattr(properties, field, getattr(form, field).data)
    return properties


class ScheduleForm(FlaskForm):
    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[Required()])
    is_not_working_day = BooleanField(
        "Завтра нерабочий день",
        validators=[Optional()],
        default=(datetime.now() + timedelta(days=1)).weekday()
        in [0, 3],  # not working mondays/thursdays by default
    )

    shipping_line = BooleanField(
        "Линия отгрузки",
        validators=[Optional()],
        default=True,
    )

    milk_project_n_boilings = StringField(
        "Количество варок в милкпроджект вчера (используется для подсчета скотты)",
        validators=[Optional()],
        default="0",
    )

    adygea_n_boilings = StringField(
        "Количество варок в адыгейском цехе вчера (используется для подсчета скотты)",
        validators=[Optional()],
        default="0",
    )
