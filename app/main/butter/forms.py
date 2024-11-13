from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import DateTimeField, FileField, IntegerField, StringField, FloatField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional, ValidationError

from app.imports.runtime import *
from app.models import *

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


class ScheduleForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    input_file = FileField("", validators=validators)
    batch_number = IntegerField("Введите номер первой партии в текущем дне", validators=[Optional()])
    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[DataRequired()])
    beg_time = StringField(
        "Время начала подготовки цеха к работе",
        validators=[Optional()],
        default="08:00",
    )
    add_full_boiling = BooleanField(
        "Вставить полную мойку внутри дня по правилу 12 часов",
        validators=[Optional()],
        default=True,
    )


class SKUButterForm(FlaskForm):
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
        super(SKUButterForm, self).__init__(*args, **kwargs)

        self.boilings = db.session.query(ButterBoiling).all()
        self.boiling.choices = list(enumerate(set([x.to_str() for x in self.boilings])))
        self.boiling.choices.append((-1, ""))

        self.groups = db.session.query(Group).all()
        self.group.choices = list(enumerate(set([x.name for x in self.groups])))
        self.group.choices.append((-1, ""))

    @staticmethod
    def validate_sku(self, name):
        sku = db.session.query(ButterSKU).filter_by(ButterSKU.name == name.data).first()
        if sku is not None:
            raise ValidationError("SKU с таким именем уже существует")


class CopySKUForm(FlaskForm):
    name = StringField("Введите имя SKU", validators=[DataRequired()])
    brand_name = StringField("Введите имя бренда", validators=[Optional()])
    code = StringField("Введите код SKU", validators=[Optional()])


class ButterBoilingTechnologyForm(FlaskForm):
    name = StringField("Название варки", validators=[Optional()])
    separator_runaway_time = IntegerField("", validators=[Optional()])
    pasteurization_time = IntegerField("", validators=[Optional()])
    increasing_temperature_time = IntegerField("", validators=[Optional()])
    submit = SubmitField(label="Сохранить")


class LineForm(FlaskForm):
    name = StringField("Введите название линии", validators=[DataRequired()])
    output_kg = IntegerField("Выход, кг", validators=[DataRequired()])
    preparing_time = IntegerField("Время подготовки", validators=[DataRequired()])
    displacement_time = IntegerField("Время смещения", validators=[DataRequired()])
    cleaning_time = IntegerField("Время чистки", validators=[DataRequired()])
    boiling_volume = IntegerField("Объем варки", validators=[DataRequired()])
    submit = SubmitField(label="Сохранить")
