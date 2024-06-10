from datetime import datetime, timedelta

from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import (
    BooleanField,
    DateTimeField,
    FileField,
    FloatField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Optional

from app.globals import db
from app.models.basic import Group
from app.models.mascarpone import MascarponeBoiling, MascarponeSKU


class UploadForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[DataRequired()])
    input_file = FileField("", validators=validators)


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
        validators=[DataRequired()],
    )


class CopySKUForm(FlaskForm):
    name = StringField("Введите имя SKU", validators=[DataRequired()])
    brand_name = StringField("Введите имя бренда", validators=[Optional()])
    code = StringField("Введите код SKU", validators=[Optional()])


class SKUMascarponeForm(FlaskForm):
    name = StringField("Введите имя SKU", validators=[DataRequired()])
    code = StringField("Введите код SKU", validators=[Optional()])
    brand_name = StringField("Введите имя бренда", validators=[Optional()])
    weight_netto = FloatField("Введите вес нетто", validators=[Optional()])
    packing_speed = IntegerField("Введите скорость фасовки", validators=[Optional()])
    shelf_life = IntegerField("Введите время хранения, д", validators=[Optional()])
    in_box = IntegerField("Введите количество упаковок в коробке, шт", validators=[Optional()])

    boiling = SelectField("Выберите тип варки", coerce=int, default=-1)
    group = SelectField("Выберите название форм фактора", coerce=int, default=-1)

    submit = SubmitField(label="Сохранить")

    def __init__(self, *args, **kwargs):
        super(SKUMascarponeForm, self).__init__(*args, **kwargs)

        self.boilings: list[MascarponeBoiling] = db.session.query(MascarponeBoiling).all()
        self.boiling.choices = list(enumerate(set(x.to_str() for x in self.boilings)))
        self.boiling.choices.append((-1, ""))

        self.groups = db.session.query(Group).all()
        self.group.choices = list(enumerate(set(x.name for x in self.groups)))
        self.group.choices.append((-1, ""))

    @staticmethod
    def validate_sku(self, name):
        sku = db.session.query(MascarponeSKU).filter_by(MascarponeSKU.name == name.data).first()
        if sku is not None:
            raise ValueError("SKU с таким именем уже существует")


class MascarponeBoilingForm(FlaskForm):

    # readonly fields
    boiling_type = StringField("Тип варки", validators=[Optional()])
    weight_netto = FloatField("Вес варки", validators=[Optional()])
    is_lactose = BooleanField("Наличие лактозы", validators=[Optional()])
    flavoring_agent = StringField("Вкусовая добавка", validators=[Optional()])
    percent = FloatField("Процент", validators=[Optional()], default=False)

    # mutable fields
    output_coeff = FloatField("Коэффициент", validators=[Optional()])
    input_kg = FloatField("Выход", validators=[Optional()])

    submit = SubmitField(label="Сохранить")


class MascarponeBoilingTechnologyForm(FlaskForm):
    name = StringField("Название варки", validators=[Optional()])
    weight = IntegerField("Введите вес, кг", validators=[Optional()])
    pouring_time = IntegerField("Введите время налива", validators=[Optional()])
    heating_time = IntegerField("Введите время нагрева", validators=[Optional()])
    analysis_time = IntegerField("Введите время анализа", validators=[Optional()])
    pumping_time = IntegerField("Введите время П", validators=[Optional()])
    ingredient_time = IntegerField("Введите время внесения ингредиентов", validators=[Optional()])
    salting_time = IntegerField("Введите время посолки", validators=[Optional()])
    separation_time = IntegerField("Введите время сепарации", validators=[Optional()])
    submit = SubmitField(label="Сохранить")


class ScheduleForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    input_file = FileField("", validators=validators)

    mascarpone_batch_number = IntegerField("Введите номер первой партии в текущем дне", validators=[Optional()])
    cream_cheese_batch_number = IntegerField("Введите номер первой партии в текущем дне", validators=[Optional()])
    # robiola_batch_number = IntegerField("Введите номер первой партии в текущем дне", validators=[Optional()])
    # cottage_cheese_batch_number = IntegerField("Введите номер первой партии в текущем дне", validators=[Optional()])
    cream_batch_number = IntegerField("Введите номер первой партии в текущем дне", validators=[Optional()])
    add_washing = BooleanField("Вставить мойку после 8 варок", default=False, validators=[Optional()])

    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[DataRequired()])
    beg_mascarpone_time = StringField(
        'Начало первой подачи линии маскарпоне"',
        validators=[Optional()],
        default="06:00",
    )
    beg_cream_cheese_time = StringField(
        'Начало первой подачи линии кремчиз"',
        validators=[Optional()],
        default="06:00",
    )


class UpdateParamsForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    input_file = FileField("", validators=validators)


class WasherForm(FlaskForm):
    name = StringField("Название мойки")
    time = IntegerField("Время мойки")


__all__ = [
    "UploadForm",
    "BoilingPlanForm",
    "CopySKUForm",
    "SKUMascarponeForm",
    "MascarponeBoilingForm",
    "MascarponeBoilingTechnologyForm",
    "ScheduleForm",
    "UpdateParamsForm",
    "WasherForm",
]
