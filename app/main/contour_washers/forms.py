from app.imports.runtime import *
from flask_wtf.file import FileRequired, FileField
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import Required, Optional
from wtforms.utils import unset_value
from app.models import *
from app.scheduler.mozzarella.properties import MozzarellaProperties
from wtforms.compat import with_metaclass, iteritems, itervalues


def create_mozzarella_form(request_form):

    class TempForm(FlaskForm):
        pass

    for k, v in json.loads(MozzarellaProperties().schema_json(indent=2))["properties"].items():

        if isinstance(v["default"], str):
            setattr(TempForm, k, StringField(
                v["description"],
                # description=v["description"],
                validators=[Optional()],
                default=v["default"]))
        elif isinstance(v["default"], list):
            setattr(TempForm, k, StringField(
                v["description"],
                # description=v["description"],
                validators=[Optional()],
                default=json.dumps(v["default"])))
        elif isinstance(v["default"], bool):
            setattr(TempForm, k, BooleanField(
                v["description"],
                # description=v["description"],
                validators=[Optional()],
                default=v))

    return TempForm(request_form)

# class MozzarellaPropertiesForm(FlaskForm):
#     bar12_present = BooleanField("bar12_present", validators=[Optional()], default=False)
#     line33_last_termizator_end_time = StringField("line33_last_termizator_end_time", validators=[Optional()], default="")
#     line36_last_termizator_end_time = StringField("line36_last_termizator_end_time", validators=[Optional()], default="")
#     line27_nine_termizator_end_time = StringField("line27_nine_termizator_end_time", validators=[Optional()], default="")
#     line27_last_termizator_end_time = StringField("line27_last_termizator_end_time", validators=[Optional()], default="")
#
#     multihead_end_time = StringField("multihead_end_time", validators=[Optional()], default="")
#     water_multihead_present = BooleanField("water_multihead_present", validators=[Optional()], default=True)
#
#     # todo: list
#     short_cleaning_times = StringField("short_cleaning_times", validators=[Optional()], default="")
#     full_cleaning_times = StringField("full_cleaning_times", validators=[Optional()], default="")
#
#     salt_melting_start_time = StringField("salt_melting_start_time", validators=[Optional()], default="")
#
#     cheesemaker1_end_time = StringField("cheesemaker1_end_time", validators=[Optional()], default="")
#     cheesemaker2_end_time = StringField("cheesemaker2_end_time", validators=[Optional()], default="")
#     cheesemaker3_end_time = StringField("cheesemaker3_end_time", validators=[Optional()], default="")
#     cheesemaker4_end_time = StringField("cheesemaker4_end_time", validators=[Optional()], default="")
#
#     water_melting_end_time = StringField("water_melting_end_time", validators=[Optional()], default="")
#     salt_melting_end_time = StringField("salt_melting_end_time", validators=[Optional()], default="")
#
#     drenator1_end_time = StringField("drenator1_end_time", validators=[Optional()], default="")
#     drenator2_end_time = StringField("drenator2_end_time", validators=[Optional()], default="")
#     drenator3_end_time = StringField("drenator3_end_time", validators=[Optional()], default="")
#     drenator4_end_time = StringField("drenator4_end_time", validators=[Optional()], default="")
#     drenator5_end_time = StringField("drenator5_end_time", validators=[Optional()], default="")
#     drenator6_end_time = StringField("drenator6_end_time", validators=[Optional()], default="")
#     drenator7_end_time = StringField("drenator7_end_time", validators=[Optional()], default="")
#     drenator8_end_time = StringField("drenator8_end_time", validators=[Optional()], default="")


class RicottaPropertiesForm(FlaskForm):
    pass


class MascarponePropertiesForm(FlaskForm):
    pass


class ButterPropertiesForm(FlaskForm):
    butter_end_time = TimeField(
        "Время окончания работы маслоцеха по умолчанию",
        validators=[Optional()],
        default=time(19, 0),
    )


class MilkProjectPropertiesForm(FlaskForm):
    milk_project_end_time = TimeField(
        "Время окончания работы милкпроджекта по умолчанию",
        validators=[Optional()],
        default=time(11, 0),
    )
    milk_project_n_boilings = StringField(
        "Количество варок в милкпроджект вчера (используется для подсчета скотты)",
        validators=[Optional()],
        default="0",
    )


class AdygeaPropertiesForm(FlaskForm):
    adygea_end_time = TimeField(
        "Время окончания работы адыгейского цеха по умолчанию",
        validators=[Optional()],
        default=time(14, 0),
    )

    adygea_n_boilings = StringField(
        "Количество варок в адыгейском цехе вчера (используется для подсчета скотты)",
        validators=[Optional()],
        default="0",
    )


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
